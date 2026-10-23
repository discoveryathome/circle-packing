"""Bounded exact rounding/maximal-radius audit of the certifier and its pinned predecessor."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import platform
import sys
import time
from decimal import localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = '978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a'
OLD_CERTIFIER = '660ee7bacb23b4554cfe5f7ebd3f1ba2e5106fd2c29c26ef623b2c4e41d603e4'
VERIFIER = '3b065d9d5140c63dcf33cad2c0ac93a0ad7afde8eb94136fb935a7e3ce5d6976'
INDEX = '889c6d4bad7cceec20319f7f30dc03746018910e58efe074b4ee95e4f9dce903'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned(path, digest):
    require(sha(path) == digest, f'hash mismatch: {path}')


pinned(ROOT/'src/verify.py', VERIFIER)
sys.path.insert(0, str(ROOT/'src'))
from verify import verify


def rounded(s, scale):
    """Exact half-even rounding for this audit's fixed-point decimal input domain."""
    negative = s.startswith('-')
    whole, _, fractional = s.lstrip('-').partition('.')
    numerator = int(whole+fractional)*scale
    denominator = 10**len(fractional)
    quotient, remainder = divmod(numerator, denominator)
    if 2*remainder > denominator or (2*remainder == denominator and quotient % 2):
        quotient += 1
    return -quotient if negative else quotient


def oracle(centers, scale):
    points = [[rounded(v, scale) for v in p] for p in centers]
    wall = min(min(x, y, scale-x, scale-y) for x, y in points)
    pair = min(((x-u)**2+(y-v)**2 for (x, y), (u, v) in itertools.combinations(points, 2)), default=None)
    low, high = 0, max(0, wall)
    while low < high:
        middle = (low+high+1)//2
        if pair is None or 4*middle*middle <= pair:
            low = middle
        else:
            high = middle-1
    return points, low


def observe(builder, centers, scale, points, radius):
    try:
        c = builder(centers, {}, scale=scale)
    except Exception as error:
        expected = radius <= 0 and isinstance(error, ValueError)
        return expected, {'exception': type(error).__name__, 'message': str(error)}, None
    actual = {'centers': c['centers'], 'radius_numerator': c['radius_numerator']}
    if radius <= 0:
        return False, dict(actual, reason='emitted a witness without positive feasible radius'), c
    expected_points = [[str(v) for v in p] for p in points]
    if c['centers'] != expected_points or c['radius_numerator'] != str(radius):
        return False, dict(actual, reason='rounding or maximal radius differs'), c
    try:
        verify(c, len(centers))
    except Exception as error:
        return False, dict(actual, reason='emitted witness failed geometry', error=str(error)), c
    larger = dict(c, radius_numerator=str(radius+1))
    try:
        verify(larger, len(centers))
    except ValueError:
        return True, actual, c
    return False, dict(actual, reason='radius+1 remained feasible'), c


def fixed_decimal(numerator, digits):
    denominator = 10**digits
    return f'{numerator//denominator}.{numerator % denominator:0{digits}d}'


def load_builder(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_certificate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True, help='checkout with the original pinned certifier')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    baseline = args.baseline.resolve()
    pinned(baseline/'src/certify.py', OLD_CERTIFIER)
    pinned(baseline/'src/verify.py', VERIFIER)
    pinned(ROOT/'discover/working-starts.json', INDEX)
    builders = {'baseline': load_builder(baseline/'src/certify.py', 'original_certifier'),
                'candidate': load_builder(ROOT/'src/certify.py', 'candidate_certifier')}
    summaries = {name: {} for name in builders}

    def case(phase, label, centers, scale):
        points, radius = oracle(centers, scale)
        emitted = {}
        for name, builder in builders.items():
            state = summaries[name].setdefault(phase, {'cases': 0, 'expected_feasible': 0,
                'expected_rejected': 0, 'matches': 0, 'failures': 0, 'first_failures': []})
            state['cases'] += 1
            state['expected_feasible' if radius > 0 else 'expected_rejected'] += 1
            matched, detail, c = observe(builder, centers, scale, points, radius)
            state['matches' if matched else 'failures'] += 1
            if not matched and len(state['first_failures']) < 50:
                state['first_failures'].append({'label': label, 'scale': str(scale), 'input': centers,
                    'expected_centers': [[str(v) for v in p] for p in points],
                    'expected_radius_numerator': str(radius), 'observed': detail})
            emitted[name] = c
        return points, radius, emitted

    grid_rows = []
    inputs = list(itertools.product(('0.1', '0.3', '0.5', '0.7', '0.9'), repeat=2))
    for scale in range(2, 33):
        count = feasible = 0
        digest = hashlib.sha256()
        for n in range(1, 5):
            for centers in itertools.combinations_with_replacement(inputs, n):
                points, radius, _ = case('grids', f'Q={scale},N={n},case={count}', centers, scale)
                digest.update((json.dumps([points, radius], separators=(',', ':'))+'\n').encode('ascii'))
                count += 1
                feasible += radius > 0
        require(count == sum(math.comb(25+n-1, n) for n in range(1, 5)), 'grid count mismatch')
        grid_rows.append({'scale': scale, 'cases': count, 'expected_feasible': feasible,
                          'expected_rejected': count-feasible, 'oracle_sha256': digest.hexdigest()})
        print(f'Q={scale}: {count} grid configurations', file=sys.stderr, flush=True)
    require(sum(row['cases'] for row in grid_rows) == 736250, 'wrong grid domain')

    for scale in range(2, 33):
        for numerator in range(1001):
            case('scalar', f'Q={scale},m={numerator}', [[fixed_decimal(numerator, 3), '0.5']], scale)
    scale = 10**15
    for k, digits, offset in itertools.product((250000000000000, 250000000000001,
                                              499999999999998, 499999999999999),
                                             (30, 79, 80, 81, 100, 200), (-1, 0, 1)):
        numerator = (2*k+1)*10**digits//(2*scale)+offset
        case('precision', f'k={k},digits={digits},offset={offset}',
             [[fixed_decimal(numerator, digits), '0.5']], scale)
    for label, x in [('above coarse tie', '0.25'+'0'*80+'1'),
                     ('below coarse tie', '0.74'+'9'*81)]:
        case('additional_controls', label, [[x, '0.5']], 2)
    with localcontext() as ctx:
        ctx.Emax = 9
        case('additional_controls', 'ambient Decimal Emax=9', [['0.5', '0.5']], 10**15)

    working = []
    index = json.loads((ROOT/'discover/working-starts.json').read_text())
    for row in index['rows']:
        path = ROOT/row['certificate']
        pinned(path, row['sha256'])
        c = json.loads(path.read_text())
        scale = int(c['denominator'])
        digits = len(c['denominator'])-1
        require(scale == 10**digits, 'working witness is not on the declared decimal grid')
        centers = [[fixed_decimal(int(v), digits) for v in p] for p in c['centers']]
        _, radius, emitted = case('working', f'N={row["n"]}', centers, scale)
        preserve = {name: all(rebuilt[key] == c[key] for key in ('n', 'denominator', 'centers', 'radius_numerator'))
                    if rebuilt is not None else False for name, rebuilt in emitted.items()}
        require(all(preserve.values()), f'working witness changed: N={row["n"]}')
        working.append(dict(row, rebuilt_radius_numerator=str(radius), stored_geometry_preserved=preserve))

    require(summaries['candidate']['scalar']['cases'] == 31031, 'wrong scalar domain')
    require(summaries['candidate']['precision']['cases'] == 72, 'wrong precision domain')
    failures = sum(phase['failures'] for phase in summaries['candidate'].values())
    result = {'status': 'author-checked; no independent review or acceptance', 'base_commit': BASE,
              'seed': 'c68557875f8ed1f9b2d61ce46a7dc42e', 'python': platform.python_version(),
              'audit_sha256': sha(Path(__file__)), 'baseline_certifier_sha256': OLD_CERTIFIER,
              'candidate_certifier_sha256': sha(ROOT/'src/certify.py'), 'verifier_sha256': VERIFIER,
              'working_index_sha256': INDEX, 'summary': summaries, 'grid_rows': grid_rows,
              'working_starts': working, 'candidate_disagreements': failures,
              'elapsed_seconds': round(time.monotonic()-start, 3),
              'not_checked': ['Unbounded inputs, all JSON/Decimal encodings or resource limits',
                              'Solver correctness, external records, novelty or optimal packing radii',
                              'Independent human review or scientific acceptance']}
    rendered = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end='')
    require(failures == 0, f'candidate disagreed on {failures} cases')
    require(summaries['baseline']['precision']['failures'] == 12, 'precision failure control changed')
    require(summaries['baseline']['additional_controls']['failures'] == 3, 'additional failure controls changed')
    require(all(summaries['baseline'][phase]['failures'] == 0 for phase in ('grids', 'scalar', 'working')),
            'baseline changed on the compatibility domain')


if __name__ == '__main__':
    main()
