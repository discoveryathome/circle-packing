#!/usr/bin/env python3
"""Bounded exact-geometry cross-check; run from any working directory."""
import argparse
import copy
import hashlib
import itertools
import json
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from verify import verify

BASE = '978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a'


def rational_geometry(c):
    """Geometry oracle for well-formed positive-denominator certificates only."""
    q = int(c['denominator'])
    radius = Fraction(int(c['radius_numerator']), q)
    points = [tuple(Fraction(int(v), q) for v in p) for p in c['centers']]
    wall = min(min(x, y, 1-x, 1-y) - radius for x, y in points)
    pair = min(((x-u)**2 + (y-v)**2 - (2*radius)**2
                for (x, y), (u, v) in itertools.combinations(points, 2)), default=None)
    valid = (radius > 0 and len(points) == c['n'] and wall >= 0
             and (pair is None or pair >= 0))
    return valid, wall, pair


def certificate(q, r, points):
    return {'schema': 'equal-circle-square/v1', 'n': len(points),
            'denominator': str(q), 'radius_numerator': str(r),
            'centers': [[str(v) for v in p] for p in points]}


def differential(c, label):
    expected, wall, pair = rational_geometry(c)
    try:
        report = verify(c, c['n'])
    except ValueError:
        if expected:
            raise AssertionError(f'{label}: valid rational geometry was rejected')
        return False
    if not expected:
        raise AssertionError(f'{label}: invalid rational geometry was accepted')
    q = int(c['denominator'])
    assert Fraction(report['radius_exact']) == Fraction(int(c['radius_numerator']), q), label
    assert Fraction(int(report['wall_slack_numerator']), int(report['wall_slack_denominator'])) == wall, label
    reported_pair = report['pair_squared_slack_numerator']
    assert (reported_pair is None) == (pair is None), label
    if pair is not None:
        assert Fraction(int(reported_pair), int(report['pair_squared_slack_denominator'])) == pair, label
        i, j = report['tightest_pair']
        assert 0 <= i < j < c['n'], label
        x, y = (Fraction(int(v), q) for v in c['centers'][i])
        u, v = (Fraction(int(v), q) for v in c['centers'][j])
        assert (x-u)**2 + (y-v)**2 - (2*Fraction(report['radius_exact']))**2 == pair, label
    else:
        assert report['tightest_pair'] is None, label
    assert report['pairs_checked'] == c['n']*(c['n']-1)//2, label
    return True


def exhaustive_grids():
    rows = []
    for n, limit in ((1, 12), (2, 12), (3, 5)):
        for q in range(1, limit+1):
            points = list(itertools.product(range(q+1), repeat=2))
            accepted = rejected = 0
            for r in range(1, q//2+2):
                for centers in itertools.combinations_with_replacement(points, n):
                    c = certificate(q, r, centers)
                    if differential(c, f'grid n={n}, q={q}, r={r}, centers={centers}'):
                        accepted += 1
                    else:
                        rejected += 1
            rows.append({'n': n, 'q': q, 'accepted': accepted, 'rejected': rejected})
            print(f'grid N={n}, Q={q}: {accepted+rejected} cases', file=sys.stderr, flush=True)
    return rows


def boundary_controls():
    cases = [
        ('single maximal circle', certificate(2, 1, [(1, 1)]), True),
        ('oblique tangency 6-8-10', certificate(20, 5, [(5, 5), (11, 13)]), True),
        ('oblique one-unit overlap', certificate(20, 5, [(5, 5), (11, 12)]), False),
        ('oblique one-unit separation', certificate(20, 5, [(5, 5), (11, 14)]), True),
        ('prime denominator', certificate(17, 2, [(2, 2), (7, 2)]), True),
        ('duplicate centers', certificate(8, 1, [(3, 3), (3, 3)]), False),
    ]
    for axis in (0, 1):
        for side, coordinate in (('lower', 0), ('upper', 4)):
            p = [2, 2]
            p[axis] = coordinate
            cases.append((f'axis {axis} {side} wall one-unit violation', certificate(4, 1, [p]), False))
    for digits in (16, 80, 200):
        q = 10**(digits-1)
        r = q//4
        c = certificate(q, r, [(r, r), (3*r, r)])
        cases.append((f'{digits}-digit denominator tangency', c, True))
        bad = copy.deepcopy(c)
        bad['centers'][1][0] = str(3*r-1)
        cases.append((f'{digits}-digit denominator one-unit overlap', bad, False))
    result = []
    for label, c, expected in cases:
        assert differential(c, label) == expected, label
        result.append({'case': label, 'accepted': expected})
    return result


def format_controls():
    base = certificate(4, 1, [(1, 1), (3, 3)])
    changes = [
        ('wrong schema', 'schema', 'other'),
        ('Boolean count', 'n', True), ('fractional count', 'n', 2.5),
        ('zero count', 'n', 0), ('count over limit', 'n', 10001),
        ('count/centers mismatch', 'n', 3),
        ('numeric denominator', 'denominator', 4),
        ('zero denominator', 'denominator', '0'),
        ('negative denominator', 'denominator', '-4'),
        ('leading-zero denominator', 'denominator', '04'),
        ('201-digit denominator', 'denominator', '1'+'0'*200),
        ('zero radius', 'radius_numerator', '0'),
        ('negative radius', 'radius_numerator', '-1'),
        ('floating radius', 'radius_numerator', 1.0),
        ('noninteger radius string', 'radius_numerator', '1.0'),
        ('nonfinite radius string', 'radius_numerator', 'NaN'),
        ('wrong coordinate arity', 'centers', [['1', '1', '1'], ['3', '3']]),
        ('numeric coordinate', 'centers', [[1, '1'], ['3', '3']]),
        ('noncanonical coordinate', 'centers', [['+1', '1'], ['3', '3']]),
    ]
    rejected = []
    for label, field, value in changes:
        c = copy.deepcopy(base)
        c[field] = value
        try:
            verify(c, 2)
        except (ValueError, KeyError, TypeError):
            rejected.append(label)
        else:
            raise AssertionError(f'format control accepted: {label}')
    try:
        verify(base, 3)
    except ValueError:
        rejected.append('expected N differs from valid certificate')
    else:
        raise AssertionError('expected N mismatch accepted')
    return rejected


def working_starts():
    index_path = ROOT / 'discover/working-starts.json'
    index = json.loads(index_path.read_text())
    rows = []
    for entry in index['rows']:
        raw = (ROOT / entry['certificate']).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == entry['sha256'], entry['certificate']
        c = json.loads(raw)
        assert c['n'] == entry['n'], entry['certificate']
        assert Fraction(int(c['radius_numerator']), int(c['denominator'])) == Fraction(entry['radius_exact'])
        assert differential(c, entry['certificate'])
        # D4 symmetries and relabelling preserve exact distances and wall margins.
        q = int(c['denominator'])
        points = [tuple(map(int, p)) for p in c['centers']]
        original = verify(c, entry['n'])
        for swap, reflect_x, reflect_y in itertools.product((False, True), repeat=3):
            transformed = []
            for x, y in reversed(points):
                if swap:
                    x, y = y, x
                transformed.append((q-x if reflect_x else x, q-y if reflect_y else y))
            moved = verify(certificate(q, int(c['radius_numerator']), transformed), entry['n'])
            for key in ('wall_slack_numerator', 'pair_squared_slack_numerator', 'pairs_checked'):
                assert moved[key] == original[key], (entry['n'], key)
        scale = 97
        scaled = verify(certificate(q*scale, int(c['radius_numerator'])*scale,
                                    [(x*scale, y*scale) for x, y in points]), entry['n'])
        assert Fraction(scaled['radius_exact']) == Fraction(original['radius_exact'])
        assert int(scaled['wall_slack_numerator']) == scale*int(original['wall_slack_numerator'])
        assert int(scaled['pair_squared_slack_numerator']) == scale**2*int(original['pair_squared_slack_numerator'])
        for wrong_n in (entry['n']-1, entry['n']+1):
            try:
                verify(c, wrong_n)
            except ValueError:
                pass
            else:
                raise AssertionError(f'working start N={entry["n"]} accepted as N={wrong_n}')
        rows.append({'n': entry['n'], 'certificate': entry['certificate'], 'sha256': digest,
                     'radius_exact': entry['radius_exact'], 'pairs_checked': original['pairs_checked'],
                     'rational_geometry_agrees': True, 'square_symmetries_with_relabelling': 8,
                     'rescaling_factor': scale, 'wrong_counts_rejected': 2,
                     'construction_credit': entry['construction_credit'], 'source': entry['source']})
        print(f'working start N={entry["n"]}: rational geometry and transformations agree', file=sys.stderr, flush=True)
    return hashlib.sha256(index_path.read_bytes()).hexdigest(), rows


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: this audit requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    controls = boundary_controls()
    formats = format_controls()
    grids = exhaustive_grids()
    index_hash, starts = working_starts()
    result = {'status': 'author-checked; no independent review or acceptance implied',
              'base_commit': BASE, 'round_seed': 'db3fcbb737f3095b0d122f377d40c7d1',
              'python': platform.python_version(),
              'verifier_sha256': hashlib.sha256((ROOT/'src/verify.py').read_bytes()).hexdigest(),
              'audit_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'working_starts_sha256': index_hash,
              'grid_domain': 'All unordered point multisets on {0,...,Q}^2, R=1,...,floor(Q/2)+1; N=1,2 for Q=1,...,12; N=3 for Q=1,...,5.',
              'grid_cases': sum(r['accepted']+r['rejected'] for r in grids),
              'grid_results': grids, 'boundary_controls': controls,
              'format_controls_rejected': formats, 'working_starts': starts,
              'disagreements': 0, 'elapsed_seconds': round(time.monotonic()-start, 3),
              'not_checked': ['All possible JSON encodings or resource-limit behavior',
                              'Solver correctness or floating-point replay',
                              'External records, pending claims, novelty or global optimality',
                              'Scientific acceptance or independent reviewer signoff']}
    rendered = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end='')
    print(f'PASS: {result["grid_cases"]} grid cases; {len(starts)} working starts; zero disagreements', file=sys.stderr)


if __name__ == '__main__':
    main()
