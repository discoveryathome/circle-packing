"""Exactly compare three pinned public Aletheia layouts; no external code execution."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from math import isqrt
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE = '978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a'
INDEX_SHA = '889c6d4bad7cceec20319f7f30dc03746018910e58efe074b4ee95e4f9dce903'
TARGETS = (600, 700, 800)
Q = 10**24
DECIMAL = re.compile(r'-?(?:0|[1-9][0-9]*)\.[0-9]{24}\Z')
sys.path.insert(0, str(ROOT/'src'))
from verify import verify


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_bytes(raw, expected):
    if digest(raw) != expected:
        raise ValueError('source hash mismatch')
    return raw


def parse(raw, expected_n):
    rows = [line.split() for line in raw.decode('utf-8').splitlines()
            if line.strip() and not line.lstrip().startswith('#')]
    if len(rows) != expected_n:
        raise ValueError('source count mismatch')
    points, radii = [], set()
    for index, row in enumerate(rows, 1):
        if len(row) != 4 or row[0] != str(index):
            raise ValueError('source columns or index sequence mismatch')
        if any(DECIMAL.fullmatch(token) is None for token in row[1:]):
            raise ValueError('expected exact 24-place decimal tokens')
        values = [Fraction(token)*Q for token in row[1:]]
        if any(value.denominator != 1 for value in values):
            raise ValueError('coordinate scale mismatch')
        x, y, radius = map(int, values)
        points.append((x, y)); radii.add(radius)
    if len(radii) != 1 or min(radii) <= 0:
        raise ValueError('inconsistent or nonpositive row radius')
    return points, radii.pop()


def limits(points):
    wall = min(Q//2-abs(value) for point in points for value in point)
    distance, pair = None, None
    for i, (x, y) in enumerate(points):
        for j in range(i):
            u, v = points[j]
            d2 = (x-u)**2+(y-v)**2
            if distance is None or d2 < distance:
                distance, pair = d2, [j+1, i+1]
    return wall, distance, pair


def rational_limits(raw):
    points = [(Fraction(row[1]), Fraction(row[2])) for row in
              (line.split() for line in raw.decode().splitlines()
               if line.strip() and not line.lstrip().startswith('#'))]
    half = Fraction(1, 2)
    wall = min(half-abs(value) for point in points for value in point)
    distance = None
    for i, (x, y) in enumerate(points):
        for u, v in points[:i]:
            candidate = (x-u)**2+(y-v)**2
            if distance is None or candidate < distance:
                distance = candidate
    return wall, distance


def grid_radius(wall, distance, digits):
    factor = 10**(digits-24)
    return min(wall*factor, isqrt(distance*factor*factor)//2)


def normalized(points, radius, digits=24, translate=True):
    factor = 10**(digits-24)
    offset = Q//2 if translate else 0
    return {'schema': 'equal-circle-square/v1', 'n': len(points),
            'denominator': str(10**digits), 'radius_numerator': str(radius),
            'centers': [[str((x+offset)*factor), str((y+offset)*factor)] for x, y in points]}


def rejected(label, operation):
    try:
        operation()
    except ValueError as error:
        return {'control': label, 'rejected': True, 'error': str(error)}
    raise AssertionError('negative control accepted: '+label)


def display(value):
    # Display only: all decisions above and below use integers or Fractions.
    with localcontext() as context:
        context.prec = 40
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def main():
    if not __debug__:
        raise RuntimeError('run this evidence audit with Python assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    manifest_raw = (PACKAGE/'source-manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    artifacts = {name: checked_bytes((args.source_dir/name).read_bytes(), item['sha256'])
                 for name, item in manifest['files'].items()}
    published_hashes = dict(line.split(None, 1)[::-1] for line in artifacts['ARTIFACTS.sha256'].decode().splitlines() if line.strip())
    for name, item in manifest['files'].items():
        if name.startswith(('data/', 'checks/')):
            assert published_hashes[name] == item['sha256']
    readme_radii = {}
    for line in artifacts['README.md'].decode().splitlines():
        match = re.match(r'^\| (600|700|800) \| ([0-9.]+)', line)
        if match:
            readme_radii[int(match[1])] = match[2]
    assert set(readme_radii) == set(TARGETS)
    index_raw = checked_bytes((ROOT/'discover/working-starts.json').read_bytes(), INDEX_SHA)
    starts = {row['n']: row for row in json.loads(index_raw)['rows']}
    records, controls = [], []
    for n in TARGETS:
        name = f'data/PACKING_N{n}_SEED_2026083001_CANDIDATE.txt'
        raw = artifacts[name]
        points, claimed = parse(raw, n)
        wall, distance, pair = limits(points)
        fraction_wall, fraction_distance = rational_limits(raw)
        assert fraction_wall == Fraction(wall, Q) and fraction_distance == Fraction(distance, Q*Q)
        original = json.loads(artifacts[f'checks/PACKING_N{n}_SEED_2026083001_EXACT_CHECK.json'])
        source_limits = original['limits']
        r24 = grid_radius(wall, distance, 24)
        r101 = grid_radius(wall, distance, 101)
        assert original['valid'] is True and original['sha256'] == manifest['files'][name]['sha256']
        assert int(source_limits['scale']) == Q and source_limits['scale_digits'] == 24 and source_limits['n'] == n
        assert int(source_limits['boundary_scaled_integer']) == wall
        assert int(source_limits['minimum_pair_squared_scaled_integer']) == distance
        assert int(source_limits['certified_radius_scaled_floor']) == r24
        assert Fraction(source_limits['certified_radius_scaled_floor_decimal']) == Fraction(r24, Q)
        public = Fraction(readme_radii[n])
        assert len(readme_radii[n].split('.')[1]) == 101 and public == Fraction(r101, 10**101)
        native = {}
        for label, radius, digits in [('row-radius', claimed, 24), ('grid-24-max', r24, 24), ('public-grid-101-max', r101, 101)]:
            c = normalized(points, radius, digits)
            report = verify(c, n)
            native[label] = dict(report, normalized_json_sha256=digest(json.dumps(c, sort_keys=True, separators=(',', ':')).encode()))
        for digits, radius in [(24, r24), (101, r101)]:
            controls.append(rejected(f'N{n}:next-unit-{digits}',
                                     lambda: verify(normalized(points, radius+1, digits), n)))
        controls.append(rejected(f'N{n}:wrong-count', lambda: verify(normalized(points, r24), n+1)))
        controls.append(rejected(f'N{n}:untranslated-centered-coordinates',
                                 lambda: verify(normalized(points, claimed, translate=False), n)))
        controls.append(rejected(f'N{n}:changed-source-byte',
                                 lambda: checked_bytes(raw[:-1]+b'X', manifest['files'][name]['sha256'])))
        controls.append(rejected(f'N{n}:truncated-rows', lambda: parse(b'\n'.join(raw.splitlines()[:-1]), n)))
        lines = raw.decode().splitlines()
        first = next(i for i, line in enumerate(lines) if line.strip() and not line.lstrip().startswith('#'))
        for label, column, token in [('duplicate-index', 0, '2'), ('nonfinite-token', 1, 'NaN'),
                                     ('inconsistent-radius', 3, '0.010000000000000000000000')]:
            altered = list(lines); tokens = altered[first].split(); tokens[column] = token
            altered[first] = ' '.join(tokens)
            altered_raw = '\n'.join(altered).encode()
            controls.append(rejected(f'N{n}:{label}', lambda: parse(altered_raw, n)))
        if n == 800:
            old = Fraction(source_limits['certified_radius_decimal'])
            assert old == Fraction(r101+1, 10**101)
            controls.append(rejected('N800:source-retracted-rounded-up-display',
                                     lambda: verify(normalized(points, int(old*10**101), 101), n)))
        else:
            assert Fraction(source_limits['certified_radius_decimal']) == public
        local = starts[n]
        local_raw = checked_bytes((ROOT/local['certificate']).read_bytes(), local['sha256'])
        local_c = json.loads(local_raw)
        local_report = verify(local_c, n)
        local_radius = Fraction(int(local_c['radius_numerator']), int(local_c['denominator']))
        assert local_radius == Fraction(local['radius_exact'])
        lower = Fraction(r101, 10**101)
        upper = Fraction(r101+1, 10**101)
        assert local_radius > upper
        cross_margin = 4*local_radius.numerator**2*Q**2-distance*local_radius.denominator**2
        assert cross_margin > 0
        records.append({'n': n, 'source_file': name, 'source_sha256': manifest['files'][name]['sha256'],
                        'coordinate_scale': str(Q), 'translation': 'x+1/2,y+1/2; radii unchanged',
                        'row_radius_exact': str(Fraction(claimed, Q)), 'pairs_per_geometry_pass': n*(n-1)//2,
                        'minimum_wall_exact': str(fraction_wall), 'minimum_pair_squared_exact': str(fraction_distance),
                        'minimum_pair_source_indices': pair, 'rational_oracle_agrees': True,
                        'native_checks': native, 'source_report_integer_minima_and_grid_floor_match': True,
                        'fixed_center_radius_lower_bound': str(lower), 'fixed_center_radius_strict_upper_bound': str(upper),
                        'corrected_public_radius': readme_radii[n],
                        'working_certificate': local['certificate'], 'working_sha256': local['sha256'],
                        'working_construction_credit': local['construction_credit'],
                        'working_radius_exact': str(local_radius), 'working_pairs_checked': local_report['pairs_checked'],
                        'working_radius_exceeds_external_fixed_center_limit': True,
                        'positive_squared_comparison_cross_product_margin': str(cross_margin),
                        'working_minus_external_radius_lower_bound': str(local_radius-upper),
                        'working_minus_external_radius_upper_bound': str(local_radius-lower),
                        'delta_lower_decimal_display': display(local_radius-upper),
                        'delta_upper_decimal_display': display(local_radius-lower)})
        print(json.dumps({'n': n, 'native_valid': True, 'rational_agrees': True,
                          'working_strictly_stronger_than_this_layout': True}), flush=True)
    report = {'status': 'author-checked numerical reconciliation; no independent review or acceptance',
              'base_commit': BASE, 'seed': 'c68557875f8ed1f9b2d61ce46a7dc42e', 'python': sys.version,
              'audit_sha256': digest(Path(__file__).read_bytes()), 'source_manifest_sha256': digest(manifest_raw),
              'verifier_sha256': digest((ROOT/'src/verify.py').read_bytes()), 'working_start_index_sha256': INDEX_SHA,
              'external_source_commit': manifest['commit'], 'external_attribution': manifest['attribution'],
              'source_files_redistributed': False, 'records': records, 'negative_controls': controls,
              'seconds': round(time.monotonic()-started, 3),
              'not_checked': ['N500 numerical pending witness; other private/new/unindexed candidates',
                              'Independent date of first public availability or maintainer receipt/acceptance',
                              'External solver correctness, execution history, optimality or universal novelty',
                              'Arbitrary import formats, metadata encodings or a license-approval determination']}
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'targets': len(records), 'negative_controls': len(controls), 'seconds': report['seconds']}))


if __name__ == '__main__':
    main()
