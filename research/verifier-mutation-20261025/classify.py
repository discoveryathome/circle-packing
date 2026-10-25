"""Differential classification of surviving verifier mutants. Standard library.

Runs the unmodified verify(), every listed mutant and spec_oracle.accepts() over one
deterministic corpus. A mutant is a DECISION fault when it accepts or rejects some corpus
input differently from the oracle while the unmodified verifier agrees with the oracle; it is
REPORT-ONLY when every decision agrees but some accepted report differs; otherwise it shows
NO DIFFERENCE on this corpus (equivalence needs a separate argument). The corpus is finite.

Executes mutated code: run it sandboxed.
    python3 research/verifier-mutation-20261025/classify.py KILL_MATRIX MUTANT_DIR --out RESULT
"""
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import random
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spec_oracle  # noqa: E402

ROOT = Path(os.environ.get('MUTATE_ROOT') or HERE.parents[1])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cert(q, r, centers, n=None):
    return {'schema': 'equal-circle-square/v1', 'n': len(centers) if n is None else n,
            'denominator': str(q), 'radius_numerator': str(r),
            'centers': [[str(x), str(y)] for x, y in centers]}


def scaled(c, k):
    s = 10 ** k
    out = copy.deepcopy(c)
    out['denominator'] = str(int(c['denominator']) * s)
    out['radius_numerator'] = str(int(c['radius_numerator']) * s)
    out['centers'] = [[str(int(v) * s) for v in p] for p in c['centers']]
    return out


def corpus():
    """Yield (label, certificate, expected_n)."""
    grid = cert(4, 1, [(1, 1), (1, 3), (3, 1), (3, 3)])
    single = cert(2, 1, [(1, 1)])
    pair = cert(10, 2, [(2, 2), (6, 2)])
    bases = {'grid': grid, 'single': single, 'pair': pair}
    for name, base in bases.items():
        n = base['n']
        for e in (None, n, n + 1, n - 1, 0, True):
            yield f'{name} expected_n={e!r}', base, e
        for value in (None, 'equal-circle-square/v2', 'equal-circle-square/v1 ', 1):
            c = copy.deepcopy(base); c['schema'] = value
            yield f'{name} schema={value!r}', c, None
        c = copy.deepcopy(base); del c['schema']
        yield f'{name} schema missing', c, None
        for value in (0, -1, True, False, float(n), str(n), None, n + 1, n - 1, 10000, 10001):
            c = copy.deepcopy(base); c['n'] = value
            yield f'{name} n={value!r}', c, None
        for field in ('denominator', 'radius_numerator'):
            v = base[field]
            for value in ('+' + v, ' ' + v, v + ' ', v + '\n', '0' + v, v + '_0', '-' + v, '-0', '0',
                          v + '.0', '', int(v), float(v), None, True, [v], chr(0x0660 + int(v[-1])) if len(v) == 1 else v):
                c = copy.deepcopy(base); c[field] = value
                yield f'{name} {field}={value!r}', c, None
            c = copy.deepcopy(base); del c[field]
            yield f'{name} {field} missing', c, None
        for i, j in itertools.product(range(n), range(2)):
            v = base['centers'][i][j]
            for value in ('+' + v, ' ' + v, v + ' ', '0' + v, v + '_0', '-' + v, '-0', '', int(v), None,
                          chr(0x0660 + int(v[-1])) if len(v) == 1 else v):
                c = copy.deepcopy(base); c['centers'][i][j] = value
                yield f'{name} center[{i}][{j}]={value!r}', c, None
        for i in range(n):
            p = base['centers'][i]
            variants = [p[0] + p[1], tuple(p), p[:1], p + ['0'], [], None, p[0]]
            if p[0] != p[1]:
                variants.append({p[0]: 0, p[1]: 1})
            for value in variants:
                c = copy.deepcopy(base); c['centers'][i] = value
                yield f'{name} center[{i}]={value!r}', c, None
        for value in (tuple(base['centers']), 'x' * n, {str(i): p for i, p in enumerate(base['centers'])},
                      base['centers'][:-1], base['centers'] + [base['centers'][0]], None):
            c = copy.deepcopy(base); c['centers'] = value
            yield f'{name} centers={type(value).__name__}:{value!r}'[:120], c, None
        c = copy.deepcopy(base); del c['centers']
        yield f'{name} centers missing', c, None
        c = copy.deepcopy(base); c['n'] = 0; c['centers'] = []
        yield f'{name} empty n=0', c, None
        digits = len(base['denominator'])
        for total in (199, 200, 201):
            yield f'{name} scaled to {total} digits', scaled(base, total - digits), None
    yield 'non-dict list', [grid], None
    yield 'non-dict string', 'grid', None
    # Exhaustive small geometry.
    for q in range(1, 5):
        for r in range(1, q + 1):
            coords = range(-1, q + 2)
            points = list(itertools.product(coords, coords))
            for p in points:
                yield f'small q={q} r={r} n=1', cert(q, r, [p]), None
            for p, s in itertools.product(points, points):
                yield f'small q={q} r={r} n=2', cert(q, r, [p, s]), None
    for q in (2, 3):
        for r in range(1, q + 1):
            points = list(itertools.product(range(q + 1), range(q + 1)))
            for trio in itertools.product(points, repeat=3):
                yield f'small q={q} r={r} n=3', cert(q, r, list(trio)), None
    # Seeded random near-contact configurations.
    rng = random.Random(20261025)
    for k in range(3000):
        q = rng.choice((10, 97, 10**6, 10**15))
        r = rng.randint(1, max(1, q // 6))
        n = rng.randint(2, 6)
        pts = [(rng.randint(r - 1, q - r + 1), rng.randint(r - 1, q - r + 1)) for _ in range(n)]
        if rng.random() < 0.5:
            # place the second point at an exact or near tangent offset from the first
            a, b = pts[0]
            dx = rng.choice((2 * r, 2 * r - 1, 0, -2 * r, -(2 * r - 1)))
            dy = 0 if dx else rng.choice((2 * r, 2 * r - 1, -2 * r, -(2 * r - 1)))
            pts[1] = (a + dx, b + dy)
        yield f'random {k} q={q} n={n}', cert(q, r, pts), None
    # A real working start and single-unit perturbations at its tightest pair and wall.
    row = min(json.loads((ROOT/'discover/working-starts.json').read_text())['rows'], key=lambda x: x['n'])
    real = json.loads((ROOT/row['certificate']).read_text())
    yield f"working start n={row['n']}", real, row['n']
    yield f"working start n={row['n']} expected n+1", real, row['n'] + 1
    for i in range(min(8, real['n'])):
        for j, d in itertools.product(range(2), (-1, 1)):
            c = copy.deepcopy(real)
            c['centers'][i][j] = str(int(c['centers'][i][j]) + d)
            yield f'working start center[{i}][{j}]{d:+d}', c, row['n']


def decide(fn, c, n):
    try:
        out = fn(copy.deepcopy(c), n)
    except Exception as e:  # any exception is a rejection; record the type
        return False, type(e).__name__, None
    if isinstance(out, dict) and out.get('valid') is True:
        return True, None, out
    return False, 'non-valid return', None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('kill_matrix')
    ap.add_argument('mutant_dir')
    ap.add_argument('--suite', default='test_verifier.py', help='classify survivors of this suite')
    ap.add_argument('--all', action='store_true', help='classify every mutant, not only survivors')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    matrix = json.loads(Path(a.kill_matrix).read_text())
    chosen = [m for m in matrix['mutants'] if m['operator'] != 'CONTROL'
              and (a.all or not m['suites'][a.suite]['killed'])]
    base = load('base_verify', ROOT/'src/verify.py').verify
    cases = list(corpus())
    base_out = [decide(base, c, n) for _, c, n in cases]
    oracle = [spec_oracle.accepts(copy.deepcopy(c), n) for _, c, n in cases]
    base_vs_oracle = [label for (label, _, _), b, o in zip(cases, base_out, oracle) if b[0] != o]
    rows = []
    for m in chosen:
        mod = load('mutant_' + m['id'], Path(a.mutant_dir)/f"{m['id']}.py")
        decision, report, error_type = [], [], []
        for (label, c, n), b, o in zip(cases, base_out, oracle):
            got = decide(mod.verify, c, n)
            if got[0] != o and b[0] == o:
                decision.append({'case': label, 'oracle_accepts': o, 'mutant_accepts': got[0]})
            elif got[0] and b[0] and got[2] != b[2]:
                diff = sorted(k for k in set(got[2]) | set(b[2]) if got[2].get(k) != b[2].get(k))
                report.append({'case': label, 'fields': diff})
            elif not got[0] and not b[0] and got[1] != b[1]:
                error_type.append({'case': label, 'base': b[1], 'mutant': got[1]})
        category = 'decision' if decision else 'report-only' if report else 'no-difference'
        rows.append({'id': m['id'], 'operator': m['operator'], 'description': m['description'],
                     'category': category, 'decision_cases': len(decision), 'report_cases': len(report),
                     'error_type_cases': len(error_type), 'first_decision': decision[:3],
                     'first_report': report[:1], 'first_error_type': error_type[:2]})
        print(m['id'], category, len(decision), len(report), len(error_type), m['description'], flush=True)
    digest = hashlib.sha256(json.dumps([[l, c, n] for l, c, n in cases], sort_keys=True, default=repr).encode()).hexdigest()
    result = {'kill_matrix_sha256': hashlib.sha256(Path(a.kill_matrix).read_bytes()).hexdigest(),
              'suite': a.suite, 'corpus_cases': len(cases), 'corpus_sha256': digest,
              'oracle_accepts': sum(oracle), 'base_disagrees_with_oracle': base_vs_oracle,
              'hashes': {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in
                         [('src/verify.py', ROOT/'src/verify.py'), ('classify.py', Path(__file__)),
                          ('spec_oracle.py', HERE/'spec_oracle.py')]},
              'mutants': rows}
    Path(a.out).write_text(json.dumps(result, indent=1) + '\n')
    print('cases', len(cases), 'oracle accepts', sum(oracle), 'base/oracle disagreements', len(base_vs_oracle))


if __name__ == '__main__':
    main()
