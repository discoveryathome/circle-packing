"""Check the hardened loader on every tracked JSON witness and one declared count-cap control."""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = '978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a'
sys.path.insert(0, str(ROOT/'src'))
from verify import load_verify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    names = subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', '-z', BASE])
    paths = sorted(name.decode() for name in names.split(b'\0') if name.endswith(b'.json'))
    rows, failures = [], []
    for name in paths:
        path = ROOT/name
        try:
            c = json.loads(path.read_bytes())
        except (ValueError, RecursionError):
            continue
        if not isinstance(c, dict) or c.get('schema') != 'equal-circle-square/v1':
            continue
        try:
            report = load_verify(path, c['n'])
        except Exception as error:
            failures.append({'path': name, 'error': type(error).__name__+': '+str(error)})
            continue
        rows.append({'path': name, 'sha256': report['sha256'], 'n': report['n'],
                     'radius_exact': report['radius_exact'], 'pairs_checked': report['pairs_checked']})
        if len(rows) % 100 == 0:
            print(f'{len(rows)} stored witnesses checked', file=sys.stderr, flush=True)

    index = json.loads((ROOT/'discover/working-starts.json').read_text())
    by_path = {row['path']: row for row in rows}
    for row in index['rows']:
        checked = by_path.get(row['certificate'])
        if checked is None or checked['sha256'] != row['sha256'] or checked['n'] != row['n']:
            failures.append({'path': row['certificate'], 'error': 'working-start binding mismatch'})

    # The 100x100 square grid is a verification-cap control, not a new packing proposal.
    c = {'schema': 'equal-circle-square/v1', 'n': 10000, 'denominator': '200',
         'radius_numerator': '1', 'centers': [[str(2*x+1), str(2*y+1)]
                                            for x in range(100) for y in range(100)]}
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/'count-cap.json'
        path.write_text(json.dumps(c))
        cap = load_verify(path, 10000)
        if cap['pairs_checked'] != 49_995_000:
            raise ValueError('wrong upper-count pair accounting')
        c['n'] = 10001
        path.write_text(json.dumps(c))
        try:
            load_verify(path, 10001)
        except ValueError as error:
            if '1..10000' not in str(error):
                raise
        else:
            raise ValueError('count above declared cap was accepted')
    result = {'status': 'author-checked; no independent review or acceptance',
              'base_commit': BASE,
              'seed': 'c68557875f8ed1f9b2d61ce46a7dc42e', 'python': platform.python_version(),
              'audit_sha256': sha(Path(__file__)), 'verifier_sha256': sha(ROOT/'src/verify.py'),
              'working_index_sha256': sha(ROOT/'discover/working-starts.json'),
              'base_json_files_scanned': len(paths), 'witnesses_checked': len(rows),
              'working_starts_checked': len(index['rows']),
              'stored_witness_pairs': sum(row['pairs_checked'] for row in rows),
              'count_cap_control': {'n': cap['n'], 'pairs_checked': cap['pairs_checked'],
                                    'sha256': cap['sha256'], 'n10001_rejected': True},
              'failures': failures, 'witnesses': rows,
              'elapsed_seconds': round(time.monotonic()-start, 3),
              'not_checked': ['Untracked/non-JSON archives, arbitrary encodings or all resource behavior',
                              'Other tools that parse JSON before calling the in-memory verifier',
                              'Solver correctness, external novelty, optimality or scientific acceptance']}
    rendered = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end='')
    if failures:
        raise ValueError(f'{len(failures)} stored-witness compatibility failures')


if __name__ == '__main__':
    main()
