"""Independent, standard-library-only exact geometric verifier. No solver imports."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def integer(s, field):
    if not isinstance(s, str) or not re.fullmatch(r'-?(0|[1-9][0-9]*)', s) or len(s) > 200:
        raise ValueError(f'{field}: expected bounded canonical integer string')
    return int(s)


def verify(c, expected_n=None):
    if c.get('schema') != 'equal-circle-square/v1':
        raise ValueError('wrong schema')
    n = c.get('n')
    if type(n) is not int or not 1 <= n <= 10000:
        raise ValueError('n must be an integer in 1..10000')
    if expected_n is not None and n != expected_n:
        raise ValueError('wrong circle count for requested instance')
    q = integer(c['denominator'], 'denominator')
    r = integer(c['radius_numerator'], 'radius')
    if q <= 0 or r <= 0 or 2*r > q:
        raise ValueError('invalid scale or radius')
    if not isinstance(c['centers'], list) or len(c['centers']) != n:
        raise ValueError('wrong number of centers')
    points = []
    min_wall = q
    for i, p in enumerate(c['centers']):
        if not isinstance(p, list) or len(p) != 2:
            raise ValueError('each center must have two coordinates')
        x, y = [integer(v, 'coordinate') for v in p]
        wall = min(x-r, y-r, q-r-x, q-r-y)
        if wall < 0:
            raise ValueError(f'wall violation at {i}')
        min_wall = min(min_wall, wall)
        points.append((x,y))
    min_pair = None
    worst_pair = None
    for i, (x,y) in enumerate(points):
        for j in range(i):
            u,v = points[j]
            slack = (x-u)**2+(y-v)**2-4*r*r
            if slack < 0:
                raise ValueError(f'overlap {j},{i}')
            if min_pair is None or slack < min_pair:
                min_pair, worst_pair = slack, [j,i]
    return {'valid': True, 'n': n, 'radius_exact': f'{r}/{q}',
            'wall_slack_numerator': str(min_wall), 'wall_slack_denominator': str(q),
            'pair_squared_slack_numerator': None if min_pair is None else str(min_pair),
            'pair_squared_slack_denominator': str(q*q), 'tightest_pair': worst_pair,
            'pairs_checked': n*(n-1)//2}


def load_verify(path, n=None):
    raw = Path(path).read_bytes()
    if len(raw) > 10_000_000:
        raise ValueError('certificate exceeds 10 MB')
    c = json.loads(raw)
    report = verify(c, n)
    report['sha256'] = hashlib.sha256(raw).hexdigest()
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('certificate')
    ap.add_argument('--n', type=int)
    args = ap.parse_args()
    try:
        print(json.dumps(load_verify(args.certificate, args.n), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as e:
        print(json.dumps({'valid': False, 'error': str(e)}))
        raise SystemExit(1)
