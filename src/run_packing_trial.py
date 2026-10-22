"""Run one prepared serial session; immutable historical optimizer, fresh output package."""
import os
# Set before importing NumPy/SciPy. One worker; no parallel arms.
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
import argparse
import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import resource
import shutil
import sys
import time
from packing_task import ROOT, check_session, read, write, sha, radius, summarize

LEGACY = ROOT/'research/contributor-20261020/code'
sys.path.insert(0, str(LEGACY))
sys.path.insert(0, str(LEGACY/'frozen'))
import numpy as np
from optimizer import from_certificate, to_unit_circles, relax, perturb, score
from certify import make_certificate, svg
from targeted import propose, elastic


def append(path, obj):
    with path.open('a') as f:
        f.write(json.dumps(obj)+'\n')


def run(directory):
    directory = Path(directory).resolve()
    s = check_session(directory)
    # Refuse reruns even after interruption. Preserve partial evidence.
    write(directory/'execution.json', {'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'session_sha256': sha(directory/'session.json'), 'python': sys.version,
          'numpy': np.__version__, 'thread_limits': {k: os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']}})
    for folder in ['certificates', 'attempt-inputs', 'images', 'best']:
        (directory/folder).mkdir()
    order = [(n, arm) for n in s['counts'] for arm in s['arms']]
    random.Random(int(s['seed'], 16)).shuffle(order)
    write(directory/'order.json', order)
    for n, arm in order:
        start_cert = read(directory/'inputs'/f'n{n}.json')
        best_c = start_cert
        best = from_certificate(start_cert)
        current = best.copy()
        seed = int.from_bytes(hashlib.sha256(f"{s['seed']}:{n}:{arm}".encode()).digest()[:16], 'big')
        rng = np.random.default_rng(seed)
        block_t, block_cpu, attempt = time.monotonic(), time.process_time(), 0
        while attempt == 0 or time.monotonic()-block_t < s['seconds_per_count_arm']-0.5:
            remaining = max(0.01, s['seconds_per_count_arm']-(time.monotonic()-block_t))
            tag = f'n{n}-{arm}-{attempt:03d}'
            t, cpu = time.monotonic(), time.process_time()
            mode = 'polish' if attempt == 0 else ['local','contact','basin'][(attempt-1)%3]
            if arm == 'targeted':
                points, mode = propose(best, current, rng, attempt)
            else:
                points = best.copy() if attempt == 0 else perturb(current, rng, mode)
            ip = directory/'attempt-inputs'/f'{tag}.json'
            write(ip, {'points': points.tolist(), 'seed': str(seed), 'mode': mode, 'attempt': attempt})
            error, soft, stats = None, {}, {}
            try:
                if arm == 'targeted' and attempt > 0:
                    points, soft = elastic(points, score(best), seconds=min(5,remaining*.35), rng=rng)
                allowance = max(.01, remaining-(time.monotonic()-t))
                points, stats = relax(points, max_steps=3000 if arm == 'polish' else 300,
                                       seconds=allowance if arm == 'polish' else min(18 if attempt == 0 else 10, allowance))
                c = make_certificate(to_unit_circles(points), {'session_seed': s['seed'], 'arm': arm,
                    'input_sha256': sha(ip), 'base_input_sha256': s['inputs'][str(n)]['sha256']})
            except Exception as exc:
                # A failed solver/certification attempt gets a logged fallback, not an invented gain.
                error = f'{type(exc).__name__}: {exc}'
                c = best_c
                points = best.copy()
            cp = directory/'certificates'/f'{tag}.json'
            write(cp, c)
            if radius(c) > radius(best_c):
                best_c, best = c, points.copy()
            accepted = radius(c) >= radius(best_c)*Fraction('0.99998') or rng.random()<.08
            current = points.copy() if accepted else best.copy()
            row = {'n': n, 'arm': arm, 'attempt': attempt, 'mode': mode, 'error': error,
                   'certificate': str(cp.relative_to(directory)), 'sha256': sha(cp),
                   'input': str(ip.relative_to(directory)), 'input_sha256': sha(ip),
                   'radius_exact': str(radius(c)), 'wall_seconds': time.monotonic()-t,
                   'cpu_seconds': time.process_time()-cpu, 'lp': stats, 'repair': soft}
            append(directory/'attempts.jsonl', row)
            attempt += 1
            if arm == 'polish':
                break
        append(directory/'blocks.jsonl', {'n': n, 'arm': arm, 'attempts': attempt,
               'wall_seconds': time.monotonic()-block_t, 'cpu_seconds': time.process_time()-block_cpu,
               'peak_rss_platform_units': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None})
        print(f'Completed N={n} {arm}: {attempt} attempts', flush=True)
    result = summarize(directory)
    for row in result['rows']:
        dst = directory/'best'/f"n{row['n']}.json"
        shutil.copyfile(directory/row['best_source'], dst)
        svg(read(dst), directory/'images'/f"n{row['n']}.svg")
    write(directory/'summary.json', result)
    check_session(directory, closed=True)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('session'); args = ap.parse_args()
    run(args.session)
