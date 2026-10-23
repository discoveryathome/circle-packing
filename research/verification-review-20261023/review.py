"""Replay pinned PR 8 and compare the finite geometry domain across Python and Node."""
import argparse
import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
import tempfile
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

BASE = '978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a'
PREDECESSOR = 'b01a3aea620366ec693adfb83bbd6d286dff73c7'
SEED = 'c68557875f8ed1f9b2d61ce46a7dc42e'
PINS = {
    'src/verify.py': '3b065d9d5140c63dcf33cad2c0ac93a0ad7afde8eb94136fb935a7e3ce5d6976',
    'discover/working-starts.json': '889c6d4bad7cceec20319f7f30dc03746018910e58efe074b4ee95e4f9dce903',
    'research/rational-check-20261022/audit.py': '26c4bb383a004271dc23441ca594039d2840cf2645961c501e0544b674faecff',
    'research/rational-check-20261022/README.md': 'c9437bb7b0a4bae0665b653d506e10ef42f7b1dd5c8bd35da812655b56044f01',
    'research/rational-check-20261022/results.json': '3bb429def43d18c243d52e0a83be8363865263d9c510f07c69998bcce16ada00',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned(path, expected):
    require(sha(path) == expected, f'hash mismatch: {path}')


pinned(ROOT/'src/verify.py', PINS['src/verify.py'])
sys.path.insert(0, str(ROOT / 'src'))
from verify import verify


def certificate(q, r, points):
    return {'schema': 'equal-circle-square/v1', 'n': len(points), 'denominator': str(q),
            'radius_numerator': str(r), 'centers': [[str(v) for v in p] for p in points]}


def signature(c, expected_n):
    try:
        report = verify(c, expected_n)
    except ValueError:
        return '0\n'
    q, r = int(c['denominator']), int(c['radius_numerator'])
    require(report['valid'] is True and report['n'] == c['n'], 'incorrect reported validity or count')
    require(Fraction(report['radius_exact']) == Fraction(r, q), 'incorrect reported radius')
    require(report['wall_slack_denominator'] == str(q), 'incorrect wall denominator')
    require(report['pair_squared_slack_denominator'] == str(q*q), 'incorrect pair denominator')
    require(report['pairs_checked'] == c['n']*(c['n']-1)//2, 'incorrect pair count')
    pair = report['pair_squared_slack_numerator']
    if c['n'] == 1:
        require(pair is None and report['tightest_pair'] is None, 'singleton pair reported')
    else:
        i, j = report['tightest_pair']
        require(0 <= i < j < c['n'], 'incorrect minimizing pair indices')
        x, y = map(int, c['centers'][i])
        u, v = map(int, c['centers'][j])
        require((x-u)**2+(y-v)**2-4*r*r == int(pair), 'incorrect minimizing pair')
    return f"1|{c['n']}|{r}|{q}|{report['wall_slack_numerator']}|{pair if pair is not None else '-'}|{report['pairs_checked']}\n"


def grids():
    rows = []
    for n, limit in ((1, 12), (2, 12), (3, 5)):
        for q in range(1, limit+1):
            points = list(itertools.product(range(q+1), repeat=2))
            digest = hashlib.sha256()
            accepted = rejected = 0
            for r in range(1, q//2+2):
                for centers in itertools.combinations_with_replacement(points, n):
                    result = signature(certificate(q, r, centers), n)
                    digest.update(result.encode('ascii'))
                    if result.startswith('1|'):
                        accepted += 1
                    else:
                        rejected += 1
            expected = math.comb((q+1)**2+n-1, n)*(q//2+1)
            require(accepted+rejected == expected, f'grid enumeration count: N={n}, Q={q}')
            rows.append({'n': n, 'q': q, 'accepted': accepted, 'rejected': rejected,
                         'signature_sha256': digest.hexdigest()})
    return rows


def controls():
    cases = []

    def add(label, q, r, points, expected, requested=None):
        c = certificate(q, r, points)
        cases.append({'label': label, 'certificate': c, 'expected': expected,
                      'expected_n': c['n'] if requested is None else requested})

    add('maximal singleton', 2, 1, [(1, 1)], True)
    add('singleton requested as two', 2, 1, [(1, 1)], False, 2)
    add('6-8-10 tangency', 20, 5, [(5, 5), (11, 13)], True)
    add('6-7 overlap', 20, 5, [(5, 5), (11, 12)], False)
    add('6-9 separation', 20, 5, [(5, 5), (11, 14)], True)
    add('duplicate centers', 8, 1, [(3, 3), (3, 3)], False)
    add('too large radius', 4, 3, [(2, 2)], False)
    add('zero radius', 4, 0, [(2, 2)], False)
    add('negative denominator', -4, 1, [(2, 2)], False)
    add('metadata count mismatch', 4, 1, [(1, 1), (3, 3)], False, 3)
    for digits in (16, 80, 200):
        q = 10**(digits-1)
        r = q//5
        for offset, valid in ((-1, False), (0, True), (1, True)):
            add(f'{digits}-digit pair offset {offset}', q, r, [(r, r), (3*r+offset, r)], valid)
        for axis, upper in itertools.product(range(2), (False, True)):
            p = [q//2, q//2]
            p[axis] = q-r+1 if upper else r-1
            add(f'{digits}-digit axis {axis} upper {upper} wall violation', q, r, [p], False)
    return cases


def working(c):
    q, r = int(c['denominator']), int(c['radius_numerator'])
    points = [tuple(map(int, p)) for p in c['centers']]
    results = [{'label': 'original', 'signature': signature(c, c['n'])}]
    require(results[0]['signature'].startswith('1|'), f"working start N={c['n']} rejected")
    for bits in range(8):
        moved = []
        for x, y in reversed(points):
            if bits & 4:
                x, y = y, x
            moved.append((q-x if bits & 2 else x, q-y if bits & 1 else y))
        result = signature(certificate(q, r, moved), c['n'])
        require(result == results[0]['signature'], 'symmetry changed exact margins')
        results.append({'label': f'symmetry-{bits}', 'signature': result})
    scaled = certificate(q*97, r*97, [(x*97, y*97) for x, y in points])
    result = signature(scaled, c['n'])
    original = results[0]['signature'].strip().split('|')
    fields = result.strip().split('|')
    require(fields[0] == '1', 'rescaled witness rejected')
    require(int(fields[4]) == 97*int(original[4]), 'wall rescaling mismatch')
    require(int(fields[5]) == 97**2*int(original[5]), 'pair rescaling mismatch')
    results.append({'label': 'scale-97', 'signature': result})
    for n in (c['n']-1, c['n']+1):
        result = signature(c, n)
        require(result == '0\n', 'wrong requested count accepted')
        results.append({'label': f'requested-{n}', 'signature': result})
    return {'n': c['n'], 'results': results}


def replay(predecessor):
    for name, expected in PINS.items():
        pinned(predecessor/name, expected)
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)/'replay.json'
        try:
            subprocess.run([sys.executable, str(predecessor/'research/rational-check-20261022/audit.py'),
                            '--output', str(output)], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            raise RuntimeError('predecessor audit failed:\n'+error.stderr) from error
        current = json.loads(output.read_text())
    saved = json.loads((predecessor/'research/rational-check-20261022/results.json').read_text())
    ignored = {'python', 'elapsed_seconds'}
    require(current.keys() == saved.keys(), 'predecessor replay fields differ')
    for key in saved.keys()-ignored:
        require(current[key] == saved[key], f'predecessor replay mismatch: {key}')
    return saved, {'compared_fields': sorted(saved.keys()-ignored),
                   'excluded_runtime_fields': sorted(ignored), 'python': current['python'],
                   'elapsed_seconds': current['elapsed_seconds']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predecessor', type=Path, required=True, help='immutable PR 8 checkout')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    for name in ('src/verify.py', 'discover/working-starts.json'):
        pinned(ROOT/name, PINS[name])
    saved, replay_result = replay(args.predecessor.resolve())
    index = json.loads((ROOT/'discover/working-starts.json').read_text())
    witnesses = []
    for row in index['rows']:
        pinned(ROOT/row['certificate'], row['sha256'])
        c = json.loads((ROOT/row['certificate']).read_text())
        require(c['n'] == row['n'], 'indexed count mismatch')
        require(Fraction(int(c['radius_numerator']), int(c['denominator'])) == Fraction(row['radius_exact']),
                'indexed radius mismatch')
        witnesses.append(c)
    cases = controls()
    try:
        node = subprocess.run(['node', str(HERE/'bigint.mjs')], input=json.dumps({'controls': cases, 'working': witnesses}),
                              check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError('BigInt audit failed:\n'+error.stderr) from error
    other = json.loads(node.stdout)
    grid_rows = grids()
    require(other['grids'] == grid_rows, 'cross-runtime grid count or signature disagreement')
    require([{k: row[k] for k in ('n', 'q', 'accepted', 'rejected')} for row in grid_rows] == saved['grid_results'],
            'predecessor grid counts disagree')
    require(sum(row['accepted']+row['rejected'] for row in grid_rows) == 306333, 'wrong grid domain')
    control_results = []
    for case in cases:
        result = signature(case['certificate'], case['expected_n'])
        require(result.startswith('1|') == case['expected'], f"failed control: {case['label']}")
        control_results.append({'label': case['label'], 'signature': result})
    require(other['controls'] == control_results, 'cross-runtime control disagreement')
    working_results = [working(c) for c in witnesses]
    require(other['working'] == working_results, 'cross-runtime working-witness disagreement')
    result = {'status': 'author-checked; no independent review or acceptance', 'base_commit': BASE,
              'seed': SEED, 'predecessor_pr': 'https://github.com/discoveryathome/circle-packing/pull/8',
              'predecessor_head': PREDECESSOR, 'predecessor_source_pins': PINS,
              'review_source_sha256': sha(Path(__file__)), 'bigint_source_sha256': sha(HERE/'bigint.mjs'),
              'python': platform.python_version(), 'node': other['node'], 'predecessor_replay': replay_result,
              'grid_results': grid_rows, 'grid_cases': 306333,
              'accepted': sum(row['accepted'] for row in grid_rows),
              'rejected': sum(row['rejected'] for row in grid_rows),
              'controls': [{'label': c['label'], 'accepted': c['expected']} for c in cases],
              'working_starts': [dict(row, cross_runtime=checked) for row, checked in zip(index['rows'], working_results)],
              'original_working_pairs': sum(c['n']*(c['n']-1)//2 for c in witnesses),
              'working_pairs_per_runtime_including_transforms': 10*sum(c['n']*(c['n']-1)//2 for c in witnesses),
              'disagreements': 0, 'elapsed_seconds': round(time.monotonic()-start, 3),
              'not_checked': ['Arbitrary N, Q, encodings, JSON parsing equivalence or resource limits',
                              'Certifier rounding/maximality, solver correctness or numerical performance',
                              'External records, novelty, global optimality or scientific acceptance',
                              'Independent human review or serial-study local package']}
    rendered = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end='')


if __name__ == '__main__':
    main()
