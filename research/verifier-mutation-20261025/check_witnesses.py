"""Re-derive the expected outcome of every witness in tests/test_verifier_faults.py. Standard library.

Uses spec_oracle.accepts() (Fractions, written from METHODS.md) for accept/reject and a direct
brute-force recomputation for the report minima. Executing the witness module imports
src/verify.py, but nothing here calls it.

    python3 research/verifier-mutation-20261025/check_witnesses.py
"""
from fractions import Fraction
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec_oracle  # noqa: E402

ROOT = Path(os.environ.get('MUTATE_ROOT') or HERE.parents[1])
TESTS = Path(os.environ.get('WITNESS_FILE') or ROOT/'tests/test_verifier_faults.py')


def report(c):
    q, r = int(c['denominator']), int(c['radius_numerator'])
    pts = [tuple(int(v) for v in p) for p in c['centers']]
    walls = [w for x, y in pts for w in (x - r, y - r, q - r - x, q - r - y)]
    pairs = {(j, i): (pts[i][0]-pts[j][0])**2 + (pts[i][1]-pts[j][1])**2 - 4*r*r
             for i in range(len(pts)) for j in range(i)}
    least = min(pairs.values())
    tight = [list(k) for k, v in pairs.items() if v == least]
    return {'radius': Fraction(r, q), 'wall_slack': min(walls), 'pair_slack': least,
            'tightest_pairs': tight, 'pairs': len(pairs)}


def report_walls(c):
    q, r = int(c['denominator']), int(c['radius_numerator'])
    return [min(x - r, y - r, q - r - x, q - r - y) for x, y in ((int(u), int(v)) for u, v in c['centers'])]


def main():
    spec = importlib.util.spec_from_file_location('witnesses', TESTS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows, bad = [], []
    for group, items in module.WITNESSES.items():
        for label, c, n, accepted in items:
            oracle = spec_oracle.accepts(c, n)
            rows.append({'group': group, 'label': label, 'expected_n': n, 'accepted': accepted, 'oracle': oracle})
            if oracle != accepted:
                bad.append(f'{group}: {label}')
    c, want = module.REPORT_CASE, module.REPORT_EXPECTED
    got = report(c)
    q = int(c['denominator'])
    walls = report_walls(c)
    checks = {
        'oracle accepts report case': spec_oracle.accepts(c, len(c['centers'])),
        'wall slack': Fraction(got['wall_slack'], q) == want['wall_slack'],
        'unique wall minimum, neither first nor last circle': walls.count(min(walls)) == 1 and walls.index(min(walls)) not in (0, len(walls) - 1),
        'pair slack': Fraction(got['pair_slack'], q*q) == want['pair_squared_slack'],
        'unique tightest pair': got['tightest_pairs'] == [want['tightest_pair']],
        'tightest pair neither first nor last in loop order': want['tightest_pair'] not in ([0, 1], [len(walls) - 2, len(walls) - 1]),
    }
    bad += [k for k, ok in checks.items() if not ok]
    print(json.dumps({'witnesses': len(rows), 'accepted': sum(r['accepted'] for r in rows),
                      'oracle_disagreements': [b for b in bad if ':' in b], 'report_checks': checks,
                      'valid': not bad}, indent=1))
    raise SystemExit(1 if bad else 0)


if __name__ == '__main__':
    main()
