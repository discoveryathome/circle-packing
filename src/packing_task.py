"""Exact working-baseline checks and immutable serial-trial preparation. Standard library."""
import argparse
import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import secrets
import shutil

from verify import load_verify, verify

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'research/readiness-20261021/serial-protocol.json'
INDEX = ROOT / 'discover/working-starts.json'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as f:
        f.write(json.dumps(value, indent=2) + '\n')


def radius(c):
    return Fraction(int(c['radius_numerator']), int(c['denominator']))


def gate(r):
    return max(Fraction('1e-10'), Fraction('1e-8') * r)


def comparison(candidate, start, n):
    verify(candidate, n)
    verify(start, n)
    r, old = radius(candidate), radius(start)
    return {'n': n, 'radius_exact': str(r), 'start_radius_exact': str(old),
            'gain_exact': str(r-old), 'gate_exact': str(gate(old)),
            'meaningful': r-old > gate(old), 'novelty': 'not assessed'}


def starts():
    rows = read(INDEX)['rows']
    if len({r['n'] for r in rows}) != len(rows):
        raise ValueError('duplicate working count')
    for r in rows:
        path = ROOT / r['certificate']
        checked = load_verify(path, r['n'])
        if checked['sha256'] != r['sha256'] or Fraction(checked['radius_exact']) != Fraction(r['radius_exact']):
            raise ValueError('working start binding mismatch')
        old = ROOT / r['previous_certificate']
        if sha(old) != r['previous_sha256']:
            raise ValueError('previous witness changed')
        load_verify(old, r['n'])
        if radius(read(path)) < radius(read(old)):
            raise ValueError('working start regresses')
    return rows


def bound_path(directory, name):
    path = (directory / name).resolve()
    if not path.is_relative_to(directory.resolve()):
        raise ValueError('path escapes session')
    return path


def required_sources():
    files = [Path('src/packing_task.py'), Path('src/run_packing_trial.py'), Path('src/verify.py'),
             Path('requirements.txt'), PROTOCOL.relative_to(ROOT), INDEX.relative_to(ROOT),
             Path('research/contributor-20261020/code/targeted.py')]
    files += [x.relative_to(ROOT) for x in sorted((ROOT/'research/contributor-20261020/code/frozen').glob('*.py'))]
    files += [Path(f'certificates/baseline/n{k}.json') for n in read(PROTOCOL)['counts'] for k in (n-1,n+1)]
    return files


def check_session(directory, closed=False):
    directory = Path(directory).resolve()
    s = read(directory/'session.json')
    protocol = read(PROTOCOL)
    if type(s['smoke']) is not bool or s['counts'] != ([500] if s['smoke'] else protocol['counts']) or s['arms'] != protocol['arms']:
        raise ValueError('session does not match declared task')
    if s['seconds_per_count_arm'] != (0.2 if s['smoke'] else protocol['search_seconds_per_count_arm']):
        raise ValueError('session budget changed')
    if not 1 <= s['session_number'] <= protocol['sessions']:
        raise ValueError('session number outside protocol')
    if set(s['inputs']) != {str(n) for n in s['counts']}:
        raise ValueError('input count mismatch')
    if (directory/'execution.json').exists() and read(directory/'execution.json')['session_sha256'] != sha(directory/'session.json'):
        raise ValueError('executed session declaration changed')
    if set(s['code_and_protocol_hashes']) != {str(p) for p in required_sources()}:
        raise ValueError('incomplete implementation/input bindings')
    for name, h in s['code_and_protocol_hashes'].items():
        if sha(ROOT/name) != h:
            # Accept only the exact operational-document migration, checking both
            # current bytes and the frozen original. Scientific edits still fail.
            import importlib.util
            helper = ROOT/'research/participation-20261022/verify.py'
            if not helper.is_file():
                raise ValueError('changed protocol or implementation: '+name)
            spec = importlib.util.spec_from_file_location('participation_history', helper)
            history = importlib.util.module_from_spec(spec); spec.loader.exec_module(history)
            if sha(history.resolve(name, h, ROOT)) != h:
                raise ValueError('changed protocol or implementation: '+name)
    for n, item in s['inputs'].items():
        p = bound_path(directory, item['path'])
        if sha(p) != item['sha256']:
            raise ValueError('session input changed')
        load_verify(p, int(n))
    if s['previous']:
        previous = ROOT/s['previous']['path']
        if previous.resolve() == directory:
            raise ValueError('cyclic session')
        previous_session = read(previous/'session.json')
        if previous_session['session_number'] != s['session_number']-1 or previous_session['smoke'] or s['smoke']:
            raise ValueError('invalid predecessor')
        check_session(previous, closed=True)
        for n, item in s['inputs'].items():
            if sha(previous/'best'/f'n{n}.json') != item['sha256']:
                raise ValueError('inherited start is not previous best')
        if sha(previous/'summary.json') != s['previous']['summary_sha256']:
            raise ValueError('previous result changed')
    else:
        if s['session_number'] != 1:
            raise ValueError('missing predecessor')
        expected = {str(r['n']): r['sha256'] for r in starts()}
        if any(item['sha256'] != expected[n] for n,item in s['inputs'].items()):
            raise ValueError('initial starts differ from working baseline')
    if closed:
        if not (directory/'execution.json').exists():
            raise ValueError('missing execution declaration')
        actual = summarize(directory)
        if read(directory/'summary.json') != actual:
            raise ValueError('summary does not match exact attempts')
        for row in actual['rows']:
            p = directory/'best'/f"n{row['n']}.json"
            load_verify(p, row['n'])
            if sha(p) != row['best_sha256']:
                raise ValueError('next starting witness changed')
    return s


def prepare(directory, previous=None, smoke=False):
    directory = Path(directory).resolve()
    directory.relative_to(ROOT)
    rows = {r['n']: r for r in starts()}
    p = read(PROTOCOL)
    counts = [500] if smoke else p['counts']
    previous_binding = None
    number = 1
    if previous:
        previous = Path(previous).resolve()
        old = check_session(previous, closed=True)
        if old['smoke'] or smoke:
            raise ValueError('smoke sessions cannot enter serial study')
        number = old['session_number'] + 1
        if number > p['sessions']:
            raise ValueError('serial study budget exhausted')
        previous_binding = {'path': str(previous.relative_to(ROOT)), 'summary_sha256': sha(previous/'summary.json')}
    paths = {n: previous/'best'/f'n{n}.json' if previous else ROOT/rows[n]['certificate'] for n in counts}
    hashes = {str(x): sha(ROOT/x) for x in required_sources()}
    directory.mkdir(parents=True, exist_ok=False)
    (directory/'inputs').mkdir()
    inputs = {}
    for n, src in paths.items():
        dst = directory/'inputs'/f'n{n}.json'
        shutil.copyfile(src, dst)
        inputs[str(n)] = {'path': str(dst.relative_to(directory)), 'sha256': sha(dst), 'source': str(src.relative_to(ROOT))}
    s = {'version': 1, 'session_number': number, 'smoke': smoke,
         'prepared_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'seed': secrets.token_hex(16), 'counts': counts, 'arms': p['arms'],
         'seconds_per_count_arm': 0.2 if smoke else p['search_seconds_per_count_arm'],
         'previous': previous_binding, 'inputs': inputs, 'code_and_protocol_hashes': hashes,
         'credit': 'Inherited original construction authors in discover/working-starts.json; record contributor identity and prior context in HANDOFF.md.'}
    write(directory/'session.json', s)
    (directory/'HANDOFF.md').write_text('# Contributor handoff\n\nFill in contributor identity/role, prior exposure, orientation and reporting time,\ncommands, failures and interpretation. Numerical logs alone do not measure onboarding.\nDo not label a same-author replay independent. No external record acceptance implied.\n')
    return s


def summarize(directory):
    directory = Path(directory).resolve()
    s = read(directory/'session.json')
    blocks = [json.loads(x) for x in (directory/'blocks.jsonl').read_text().splitlines()]
    trials = [json.loads(x) for x in (directory/'attempts.jsonl').read_text().splitlines()]
    expected = {(n, arm) for n in s['counts'] for arm in s['arms']}
    if len(blocks) != len(expected) or {(b['n'], b['arm']) for b in blocks} != expected:
        raise ValueError('partial/duplicate session blocks')
    best = {n: bound_path(directory, s['inputs'][str(n)]['path']) for n in s['counts']}
    input_hashes = {n: sha(path) for n, path in best.items()}
    arm_best = {(n, arm): read(best[n]) for n, arm in expected}
    polish = {n: radius(read(best[n])) for n in s['counts']}
    seen = set()
    for t in trials:
        if (t['n'], t['arm']) not in expected or t['certificate'] in seen:
            raise ValueError('unexpected or duplicate attempt')
        seen.add(t['certificate'])
        path = bound_path(directory, t['certificate'])
        start = bound_path(directory, t['input'])
        if sha(path) != t['sha256'] or sha(start) != t['input_sha256']:
            raise ValueError('attempt hash mismatch')
        c = read(path)
        verify(c, t['n'])
        r = radius(c)
        if str(r) != t['radius_exact']:
            raise ValueError('false attempted radius')
        key = (t['n'], t['arm'])
        if t['error'] is None:
            provenance = c.get('provenance')
            bindings = {'session_seed': s['seed'], 'arm': t['arm'],
                        'input_sha256': t['input_sha256'],
                        'base_input_sha256': input_hashes[t['n']]}
            if not isinstance(provenance, dict) or any(provenance.get(k) != v for k, v in bindings.items()):
                raise ValueError('attempt provenance does not match session/input')
        elif not isinstance(t['error'], str) or not t['error'] or c != arm_best[key]:
            raise ValueError('failed attempt does not retain its arm best')
        if r > radius(arm_best[key]):
            arm_best[key] = c
        if r > radius(read(best[t['n']])):
            best[t['n']] = path
        if t['arm'] == 'polish':
            polish[t['n']] = max(polish[t['n']], r)
    for b in blocks:
        group = [t for t in trials if t['n'] == b['n'] and t['arm'] == b['arm']]
        if not group or b['attempts'] != len(group):
            raise ValueError('block attempt accounting mismatch')
    rows = []
    for n, path in best.items():
        start = read(bound_path(directory, s['inputs'][str(n)]['path']))
        row = comparison(read(path), start, n)
        row.update({'best_source': str(path.relative_to(directory)), 'best_sha256': sha(path),
                    'polish_radius_exact': str(polish[n]),
                    'beyond_polish_gate': radius(read(path))-polish[n] > gate(radius(start))})
        rows.append(row)
    return {'session_number': s['session_number'], 'smoke': s['smoke'], 'rows': rows,
            'attempts': len(trials), 'blocks': len(blocks), 'session_sha256': sha(directory/'session.json'),
            'attempts_sha256': sha(directory/'attempts.jsonl'), 'blocks_sha256': sha(directory/'blocks.jsonl'),
            'solver_or_certificate_errors': sum(t['error'] is not None for t in trials), 'evidence': 'author-run unless independently reviewed; local feasibility only'}


def study(last):
    chain = []
    directory = Path(last).resolve()
    for expected in [3, 2, 1]:
        s = check_session(directory, closed=True)
        if s['smoke'] or s['session_number'] != expected:
            raise ValueError('requires all three full serial sessions')
        chain.append(read(directory/'summary.json'))
        if s['previous']:
            directory = ROOT/s['previous']['path']
    gained = [x for x in chain if any(r['meaningful'] for r in x['rows'])]
    counts = sorted({r['n'] for x in chain for r in x['rows'] if r['meaningful']})
    later = any(r['meaningful'] and r['beyond_polish_gate'] for x in chain if x['session_number'] > 1 for r in x['rows'])
    return {'sessions_with_gain': len(gained), 'distinct_counts_with_gain': counts,
            'later_nonpolish_gain': later,
            'product_gate_passed': len(gained) >= 2 and len(counts) >= 2 and later,
            'errors': sum(x['solver_or_certificate_errors'] for x in chain),
            'scope': 'Local fixed-portfolio productivity only; independent review, onboarding, external standing and launch decision remain pending.'}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='command', required=True)
    sub.add_parser('check')
    c = sub.add_parser('compare'); c.add_argument('witness'); c.add_argument('--n', required=True, type=int); c.add_argument('--start')
    p = sub.add_parser('prepare'); p.add_argument('--out', required=True); p.add_argument('--previous'); p.add_argument('--smoke', action='store_true')
    v = sub.add_parser('verify-session'); v.add_argument('directory')
    st = sub.add_parser('study'); st.add_argument('--last', required=True)
    a = ap.parse_args()
    if a.command == 'check':
        print(json.dumps({'valid': True, 'working_counts': [r['n'] for r in starts()], 'intake': 'open'}))
    elif a.command == 'compare':
        default = next(r for r in starts() if r['n'] == a.n)
        baseline = Path(a.start) if a.start else ROOT/default['certificate']
        print(json.dumps(comparison(read(a.witness), read(baseline), a.n), indent=2))
    elif a.command == 'prepare':
        print(json.dumps(prepare(a.out, a.previous, a.smoke), indent=2))
    elif a.command == 'study':
        print(json.dumps(study(a.last), indent=2))
    else:
        check_session(a.directory, closed=True)
        print(json.dumps({'valid': True, 'session': a.directory, 'novelty': 'not assessed'}))


if __name__ == '__main__':
    main()
