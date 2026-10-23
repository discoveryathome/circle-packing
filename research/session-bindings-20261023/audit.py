"""Bounded session provenance/fallback controls; no optimization or historical edits."""
import argparse
import copy
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[2]
BASE = '978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a'
ARMS = ('polish', 'original', 'targeted')
SEED = 'c68557875f8ed1f9b2d61ce46a7dc42e'
HISTORICAL = ROOT/'research/readiness-20261021/smoke'
sys.path.insert(0, str(ROOT/'src'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2)+'\n').encode()


def baseline_bytes(name):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{BASE}:{name}'])


def modules():
    if (ROOT/'src/verify.py').read_bytes() != baseline_bytes('src/verify.py'):
        raise ValueError('replay this audit at its own PR head, with the unchanged base verifier')
    original_raw = baseline_bytes('src/packing_task.py')
    original = types.ModuleType('original_packing_task')
    original.__file__ = str(ROOT/'src/packing_task.py')
    exec(compile(original_raw, 'base:src/packing_task.py', 'exec'), original.__dict__)
    spec = importlib.util.spec_from_file_location('candidate_packing_task', ROOT/'src/packing_task.py')
    candidate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate)
    return original, candidate, digest(original_raw)


def logs(directory, rows):
    (directory/'attempts.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in rows))
    blocks = [{'n': 4, 'arm': arm, 'attempts': sum(t['arm'] == arm for t in rows)} for arm in ARMS]
    (directory/'blocks.jsonl').write_text(''.join(json.dumps(b)+'\n' for b in blocks))


def cert(radius):
    return {'schema': 'equal-circle-square/v1', 'n': 4, 'denominator': '100',
            'radius_numerator': str(radius),
            'centers': [['25', '25'], ['25', '75'], ['75', '25'], ['75', '75']]}


def synthetic(directory):
    for name in ('inputs', 'attempt-inputs', 'certificates'):
        (directory/name).mkdir()
    start = cert(20)
    start['provenance'] = {'source': 'synthetic inherited start'}
    raw = encoded(start)
    (directory/'inputs/n4.json').write_bytes(raw)
    base_hash = digest(raw)
    session = {'counts': [4], 'arms': list(ARMS), 'inputs': {'4': {'path': 'inputs/n4.json'}},
               'session_number': 1, 'smoke': False, 'seed': SEED}
    (directory/'session.json').write_bytes(encoded(session))
    templates, successes = {}, {}
    for arm in ARMS:
        for index in (0, 1):
            tag = f'{arm}-{index}'
            ip = directory/'attempt-inputs'/f'{tag}.json'
            ip.write_bytes(encoded({'points': [[.25, .25], [.25, .75], [.75, .25], [.75, .75]],
                                    'attempt': index, 'arm': arm}))
            input_hash = digest(ip.read_bytes())
            templates[arm, index] = {'n': 4, 'arm': arm, 'attempt': index,
                'certificate': f'certificates/{tag}.json', 'input': str(ip.relative_to(directory)),
                'input_sha256': input_hash}
            for radius in (19, 20, 21, 22):
                c = cert(radius)
                c['provenance'] = {'session_seed': SEED, 'arm': arm, 'input_sha256': input_hash,
                                   'base_input_sha256': base_hash}
                successes[arm, index, radius] = c
    return start, templates, successes


def materialize(directory, schedule, states, start, templates, successes):
    best = {arm: start for arm in ARMS}
    rows = []
    for (arm, index), state in zip(schedule, states):
        failed = state == 'error'
        c = best[arm] if failed else successes[arm, index, state]
        if not failed and int(c['radius_numerator']) > int(best[arm]['radius_numerator']):
            best[arm] = c
        row = dict(templates[arm, index], error='RuntimeError: controlled failure' if failed else None)
        raw = encoded(c)
        (directory/row['certificate']).write_bytes(raw)
        row.update(sha256=digest(raw), radius_exact=str(Fraction(int(c['radius_numerator']), 100)))
        rows.append(row)
    logs(directory, rows)
    return rows


def reject_control(label, directory, original, candidate, records):
    outcomes = []
    for module in (original, candidate):
        try:
            module.summarize(directory)
            outcomes.append({'accepted': True})
        except ValueError as error:
            outcomes.append({'accepted': False, 'error': str(error)})
    if not outcomes[0]['accepted'] or outcomes[1]['accepted']:
        raise AssertionError((label, outcomes))
    records.append({'control': label, 'original': outcomes[0], 'candidate': outcomes[1]})


def real_controls(directory, original, candidate):
    shutil.copytree(HISTORICAL, directory)
    source_rows = [json.loads(line) for line in (directory/'attempts.jsonl').read_text().splitlines()]
    sources = {row['certificate']: (directory/row['certificate']).read_bytes() for row in source_rows}
    records = []
    for index, source in enumerate(source_rows):
        for field in ('session_seed', 'arm', 'input_sha256', 'base_input_sha256'):
            for action in ('mismatch', 'missing'):
                rows = copy.deepcopy(source_rows)
                c = json.loads(sources[source['certificate']])
                if action == 'missing':
                    del c['provenance'][field]
                else:
                    c['provenance'][field] = 'controlled mismatch'
                raw = encoded(c)
                (directory/source['certificate']).write_bytes(raw)
                rows[index]['sha256'] = digest(raw)
                (directory/'attempts.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in rows))
                reject_control(f"{source['arm']}:{action}:{field}", directory, original, candidate, records)
                (directory/source['certificate']).write_bytes(sources[source['certificate']])
        for action, value in [('missing-object', None), ('null', None), ('list', []), ('string', 'metadata'), ('number', 1)]:
            rows = copy.deepcopy(source_rows)
            c = json.loads(sources[source['certificate']])
            if action == 'missing-object':
                del c['provenance']
            else:
                c['provenance'] = value
            raw = encoded(c)
            (directory/source['certificate']).write_bytes(raw)
            rows[index]['sha256'] = digest(raw)
            (directory/'attempts.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in rows))
            reject_control(f"{source['arm']}:provenance:{action}", directory, original, candidate, records)
            (directory/source['certificate']).write_bytes(sources[source['certificate']])
    return records


def fallback_controls(directory, original, candidate, start, templates, successes):
    schedule = [(arm, index) for arm in ARMS for index in (0, 1)]
    records = []
    for arm in ARMS:
        for stage in ('initial', 'improved', 'tie'):
            states = [21]*6
            offset = schedule.index((arm, 0))
            states[offset] = 22 if stage != 'initial' else 'error'
            states[offset+1] = 'error'
            rows = materialize(directory, schedule, states, start, templates, successes)
            target = offset if stage == 'initial' else offset+1
            correct = json.loads((directory/rows[target]['certificate']).read_text())
            variants = []
            for radius in (19, 20, 21, 22):
                if radius != int(correct['radius_numerator']):
                    changed = copy.deepcopy(correct); changed['radius_numerator'] = str(radius)
                    variants.append((f'radius-{radius}', changed))
            changed = copy.deepcopy(correct); changed['provenance']['changed'] = True
            variants.append(('metadata', changed))
            if stage == 'tie':
                # A successful tie creates new provenance, but does not replace the fallback best.
                states[offset+1] = 22
                rows = materialize(directory, schedule, states, start, templates, successes)
                rows[target]['error'] = 'RuntimeError: controlled failure'
                changed = copy.deepcopy(successes[arm, 1, 22])
                variants = [('last-tie-provenance', changed)]
            for label, changed in variants:
                raw = encoded(changed)
                (directory/rows[target]['certificate']).write_bytes(raw)
                rows[target].update(sha256=digest(raw), radius_exact=str(Fraction(int(changed['radius_numerator']), 100)))
                logs(directory, rows)
                reject_control(f'{arm}:{stage}:{label}', directory, original, candidate, records)
        states = ['error']*6
        rows = materialize(directory, schedule, states, start, templates, successes)
        target = schedule.index((arm, 0))
        for label, error in [('empty', ''), ('false', False), ('zero', 0), ('list', []), ('object', {})]:
            rows[target]['error'] = error
            logs(directory, rows)
            reject_control(f'{arm}:error-{label}', directory, original, candidate, records)
    return records


def sequence_checks(directory, original, candidate, start, templates, successes):
    cases = meaningful = successes_count = failures_count = 0
    stream = hashlib.sha256()
    for order in itertools.permutations(ARMS):
        schedule = [(arm, index) for arm in order for index in (0, 1)]
        for states in itertools.product(('error', 19, 20, 21, 22), repeat=6):
            materialize(directory, schedule, states, start, templates, successes)
            successful = [state for state in states if state != 'error']
            expected_radius = max([20]+successful)
            expected_polish = max([20]+[state for (arm, _), state in zip(schedule, states)
                                       if arm == 'polish' and state != 'error'])
            errors = states.count('error')
            results = [module.summarize(directory) for module in (original, candidate)]
            if results[0] != results[1]:
                raise AssertionError(('summary disagreement', order, states))
            row = results[1]['rows'][0]
            expected = {'radius_exact': str(Fraction(expected_radius, 100)),
                        'polish_radius_exact': str(Fraction(expected_polish, 100)),
                        'meaningful': expected_radius > 20, 'beyond_polish_gate': expected_radius > expected_polish}
            if any(row[key] != value for key, value in expected.items()) or results[1]['solver_or_certificate_errors'] != errors:
                raise AssertionError(('oracle disagreement', order, states, expected))
            cases += 1
            meaningful += expected_radius > 20
            successes_count += len(successful)
            failures_count += errors
            stream.update(json.dumps([order, states, expected_radius, expected_polish, errors], separators=(',', ':')).encode()+b'\n')
            if cases % 10000 == 0:
                print(json.dumps({'valid_sequences_checked': cases}), flush=True)
    assert cases == 6*5**6 and meaningful == 6*(5**6-3**6)
    assert successes_count == 6*6*4*5**5 and failures_count == 6*6*5**5
    return {'arm_orders': 6, 'states_per_attempt': ['error', 19, 20, 21, 22], 'attempts_per_arm': 2,
            'cases_per_implementation': cases, 'successful_attempts_per_implementation': successes_count,
            'fallback_attempts_per_implementation': failures_count, 'meaningful_cases': meaningful,
            'attempt_pairs_per_implementation': cases*6*6, 'case_stream_sha256': stream.hexdigest(),
            'summary_or_oracle_disagreements': 0}


def main():
    if not __debug__:
        raise RuntimeError('run this evidence audit with Python assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    original, candidate, original_hash = modules()
    saved = json.loads((HISTORICAL/'summary.json').read_text())
    assert original.summarize(HISTORICAL) == saved == candidate.summarize(HISTORICAL)
    historical_hashes = {str(p.relative_to(HISTORICAL)): digest(p.read_bytes())
                         for p in sorted(HISTORICAL.rglob('*')) if p.is_file()}
    with tempfile.TemporaryDirectory(prefix='session-binding-audit-', dir=ROOT.parent) as temp:
        temp = Path(temp)
        real = real_controls(temp/'real', original, candidate)
        synthetic_root = temp/'synthetic'; synthetic_root.mkdir()
        start, templates, successes = synthetic(synthetic_root)
        fallback = fallback_controls(synthetic_root, original, candidate, start, templates, successes)
        sequences = sequence_checks(synthetic_root, original, candidate, start, templates, successes)
    assert historical_hashes == {str(p.relative_to(HISTORICAL)): digest(p.read_bytes())
                                for p in sorted(HISTORICAL.rglob('*')) if p.is_file()}
    report = {'status': 'author-checked; no independent review or acceptance', 'base_commit': BASE, 'seed': SEED,
              'python': sys.version, 'original_checker_sha256': original_hash,
              'candidate_checker_sha256': digest((ROOT/'src/packing_task.py').read_bytes()),
              'audit_sha256': digest(Path(__file__).read_bytes()),
              'unchanged_verifier_sha256': digest((ROOT/'src/verify.py').read_bytes()),
              'historical_smoke': {'attempts': 3, 'saved_summary_exactly_reproduced': True,
                                    'source_files_unchanged': True, 'file_sha256': historical_hashes},
              'real_provenance_controls': real, 'synthetic_fallback_controls': fallback,
              'valid_sequence_domain': sequences, 'seconds': round(time.monotonic()-started, 3),
              'not_checked': ['Unavailable retained 317-attempt serial-study archive',
                              'Solver execution/authenticity, numerical correctness, timing or causality',
                              'Arbitrary JSON representations, unbounded event sequences or all metadata types',
                              'Scientific acceptance, external standing, novelty or optimality']}
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'cases': sequences['cases_per_implementation'], 'negative_controls': len(real)+len(fallback),
                      'disagreements': 0, 'seconds': report['seconds']}))


if __name__ == '__main__':
    main()
