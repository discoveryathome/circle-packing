"""Single-point mutation analysis of the exact verifier's decision functions. Standard library.

Generates mutants of integer() and verify() in src/verify.py with a declared operator set,
runs each named unittest suite against every mutant in a disposable copy of the checkout,
and writes a JSON kill matrix. It never edits the checkout it reads from.

    python3 research/verifier-mutation-20261025/mutate.py --out OUT [--bwrap] \
        --suite test_verifier.py --suite test_packing_task.py

--bwrap runs every suite inside bubblewrap with no network and the home directory hidden.
Mutant sources are written to OUT/mutants/ for classify.py.
"""
import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(os.environ.get('MUTATE_ROOT') or Path(__file__).resolve().parents[2])
TARGET = 'src/verify.py'
FUNCTIONS = ('integer', 'verify')
REGEX = r'-?(0|[1-9][0-9]*)'
REGEX_VARIANTS = [
    (r'(0|[1-9][0-9]*)', 'drop optional minus sign'),
    (r'-?([0-9]+)', 'allow leading zeros'),
    (r'-?([1-9][0-9]*)', 'reject zero'),
    (r'-?(0|[0-9][0-9]*)', 'allow leading zeros via second branch'),
    (r'-?(0|[1-9][0-9]*)\s*', 'allow trailing whitespace'),
]
ROR = {ast.Lt: (ast.LtE, ast.GtE), ast.LtE: (ast.Lt, ast.Gt), ast.Gt: (ast.GtE, ast.LtE),
       ast.GtE: (ast.Gt, ast.Lt), ast.Eq: (ast.NotEq,), ast.NotEq: (ast.Eq,),
       ast.Is: (ast.IsNot,), ast.IsNot: (ast.Is,), ast.In: (ast.NotIn,), ast.NotIn: (ast.In,)}
AOR = {ast.Add: (ast.Sub,), ast.Sub: (ast.Add,), ast.Mult: (ast.Add,), ast.Pow: (ast.Mult,),
       ast.FloorDiv: (ast.Mult,)}
SYMBOL = {ast.Lt: '<', ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>=', ast.Eq: '==', ast.NotEq: '!=',
          ast.Is: 'is', ast.IsNot: 'is not', ast.In: 'in', ast.NotIn: 'not in', ast.Add: '+',
          ast.Sub: '-', ast.Mult: '*', ast.Pow: '**', ast.FloorDiv: '//', ast.And: 'and', ast.Or: 'or'}


def walk(node, path=()):
    yield node, path
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, ast.AST):
                    yield from walk(item, path + ((field, i),))
        elif isinstance(value, ast.AST):
            yield from walk(value, path + ((field, None),))


def locate(root, path):
    node = root
    for field, i in path:
        node = getattr(node, field) if i is None else getattr(node, field)[i]
    return node


def replace(root, path, new):
    parent = locate(root, path[:-1])
    field, i = path[-1]
    if i is None:
        setattr(parent, field, new)
    else:
        getattr(parent, field)[i] = new


def seg(source, node):
    return ast.get_source_segment(source, node) or ast.unparse(node)


def sites(tree, source):
    """Yield (operator, description, path, builder) for every declared mutation site."""
    for top, top_path in walk(tree):
        if not (isinstance(top, ast.FunctionDef) and top.name in FUNCTIONS):
            continue
        for node, rel in walk(top):
            path = top_path + rel
            where = f'{top.name}:{getattr(node, "lineno", "?")}'
            if isinstance(node, ast.Compare):
                for k, op in enumerate(node.ops):
                    for alt in ROR.get(type(op), ()):
                        def build(n, k=k, alt=alt):
                            n.ops[k] = alt()
                            return n
                        operands = [node.left] + node.comparators
                        pair = f'{seg(source, operands[k])} {SYMBOL[type(op)]} {seg(source, operands[k+1])}'
                        yield ('ROR', f'{where} {SYMBOL[type(op)]} -> {SYMBOL[alt]} in `{pair}`', path, build)
                left = node.left
                if (len(node.ops) == 1 and isinstance(node.ops[0], ast.IsNot) and isinstance(left, ast.Call)
                        and isinstance(left.func, ast.Name) and left.func.id == 'type' and len(left.args) == 1):
                    def build(n):
                        call = ast.Call(ast.Name('isinstance', ast.Load()), [n.left.args[0], n.comparators[0]], [])
                        return ast.UnaryOp(ast.Not(), call)
                    yield ('TYPE', f'{where} exact type test -> isinstance in `{seg(source, node)}`', path, build)
            elif isinstance(node, ast.BoolOp):
                alt = ast.Or if isinstance(node.op, ast.And) else ast.And
                def build(n, alt=alt):
                    n.op = alt()
                    return n
                yield ('LCR', f'{where} {SYMBOL[type(node.op)]} -> {SYMBOL[alt]} in `{seg(source, node)}`', path, build)
                for k, value in enumerate(node.values):
                    def build(n, k=k):
                        rest = [v for i, v in enumerate(n.values) if i != k]
                        return rest[0] if len(rest) == 1 else ast.BoolOp(n.op, rest)
                    yield ('OPD', f'{where} drop operand `{seg(source, value)}` of boolean test', path, build)
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                yield ('NOT', f'{where} remove `not` in `{seg(source, node)}`', path, lambda n: n.operand)
            elif isinstance(node, ast.Constant) and type(node.value) is int:
                for delta in (1, -1):
                    yield ('CRP', f'{where} constant {node.value} -> {node.value + delta}', path,
                           lambda n, d=delta: ast.Constant(n.value + d))
            elif isinstance(node, ast.Constant) and node.value == REGEX:
                for variant, label in REGEX_VARIANTS:
                    yield ('RGX', f'{where} regex: {label}', path, lambda n, v=variant: ast.Constant(v))
            elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                  and node.value.id == 're' and node.attr == 'fullmatch'):
                for alt in ('match', 'search'):
                    def build(n, alt=alt):
                        n.attr = alt
                        return n
                    yield ('RGX', f'{where} re.fullmatch -> re.{alt}', path, build)
            elif isinstance(node, ast.BinOp):
                for alt in AOR.get(type(node.op), ()):
                    def build(n, alt=alt):
                        n.op = alt()
                        return n
                    yield ('AOR', f'{where} {SYMBOL[type(node.op)]} -> {SYMBOL[alt]} in `{seg(source, node)}`', path, build)
                yield ('OPD', f'{where} `{seg(source, node)}` -> `{seg(source, node.left)}`', path, lambda n: n.left)
                yield ('OPD', f'{where} `{seg(source, node)}` -> `{seg(source, node.right)}`', path, lambda n: n.right)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'min' and len(node.args) >= 2:
                    for k, arg in enumerate(node.args):
                        def build(n, k=k):
                            n.args = [a for i, a in enumerate(n.args) if i != k]
                            return n
                        yield ('ARG', f'{where} drop `{seg(source, arg)}` from `{seg(source, node)}`', path, build)
                if node.func.id == 'range' and len(node.args) == 1:
                    for delta, op in ((-1, ast.Sub), (1, ast.Add)):
                        def build(n, op=op):
                            n.args = [ast.BinOp(n.args[0], op(), ast.Constant(1))]
                            return n
                        yield ('ARG', f'{where} `{seg(source, node)}` bound {delta:+d}', path, build)
            if isinstance(node, ast.If):
                yield ('GRD', f'{where} remove guard `if {seg(source, node.test)}`', path + (('test', None),),
                       lambda n: ast.Constant(False))
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.Expr)) and not (
                    isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)):
                yield ('SDL', f'{where} delete statement `{seg(source, node)}`', path, lambda n: ast.Pass())


def mutants(source):
    tree = ast.parse(source)
    seen = {ast.unparse(tree) + '\n'}
    out = []
    for operator, description, path, build in sites(tree, source):
        mutant = copy.deepcopy(tree)
        replace(mutant, path, build(copy.deepcopy(locate(mutant, path))))
        ast.fix_missing_locations(mutant)
        text = ast.unparse(mutant) + '\n'
        try:
            compile(text, TARGET, 'exec')
        except SyntaxError:
            continue
        if text in seen:
            continue
        seen.add(text)
        out.append({'id': f'M{len(out)+1:03d}', 'operator': operator, 'description': description,
                    'source': text})
    return out


def control_always_accept(source):
    """Hand-written control: verify() accepts anything with the right n, no geometry."""
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'verify')
    fn.body = ast.parse("n = c.get('n')\nreturn {'valid': True, 'n': n, 'radius_exact': "
                        "f\"{c['radius_numerator']}/{c['denominator']}\", 'pairs_checked': 0}").body
    ast.fix_missing_locations(tree)
    return ast.unparse(tree) + '\n'


def sandbox_prefix(tree_dir):
    home = os.path.expanduser('~')
    return ['bwrap', '--ro-bind', '/', '/', '--tmpfs', home, '--bind', str(tree_dir), str(tree_dir),
            '--tmpfs', '/tmp', '--dev', '/dev', '--proc', '/proc', '--unshare-net', '--unshare-pid',
            '--die-with-parent', '--chdir', str(tree_dir)]


def run_suite(tree_dir, pattern, use_bwrap, timeout=300):
    # -B: write no bytecode. With no __pycache__ copied in, nothing stale can be read. A first
    # run without this reused a same-size mutant's .pyc written within the same second.
    cmd = [sys.executable, '-I', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', pattern]
    if use_bwrap:
        cmd = sandbox_prefix(tree_dir) + cmd
    try:
        p = subprocess.run(cmd, cwd=tree_dir, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {'killed': True, 'returncode': None, 'summary': 'timeout'}
    ran = re.search(r'Ran (\d+) tests?', p.stderr)
    tail = [line for line in p.stderr.strip().splitlines()[-1:]]
    return {'killed': p.returncode != 0, 'returncode': p.returncode,
            'tests_run': int(ran.group(1)) if ran else None, 'summary': tail[0] if tail else ''}


def sha(text):
    return hashlib.sha256(text.encode() if isinstance(text, str) else text).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--suite', action='append', required=True)
    ap.add_argument('--bwrap', action='store_true')
    ap.add_argument('--extra-test', action='append', default=[],
                    help='copy this test file into the disposable tree before running')
    a = ap.parse_args()
    out = Path(a.out).resolve()
    if out.is_relative_to(ROOT.resolve()):
        raise SystemExit('--out must be outside the checkout (the checkout is copied into it)')
    out.mkdir(parents=True, exist_ok=False)
    (out/'mutants').mkdir()
    source = (ROOT/TARGET).read_text()
    tree_dir = out/'tree'
    shutil.copytree(ROOT, tree_dir, ignore=shutil.ignore_patterns('.git', 'tmp', '__pycache__'))
    for extra in a.extra_test:
        shutil.copyfile(extra, tree_dir/'tests'/Path(extra).name)
    target = tree_dir/TARGET
    rows = []
    controls = [('C-unmutated', 'control: ast round-trip of the unmodified source', ast.unparse(ast.parse(source)) + '\n'),
                ('C-always-accept', 'control: verify() returns valid without any check', control_always_accept(source))]
    items = [{'id': i, 'operator': 'CONTROL', 'description': d, 'source': s} for i, d, s in controls] + mutants(source)
    try:
        for m in items:
            (out/'mutants'/f"{m['id']}.py").write_text(m['source'])
            target.write_text(m['source'])
            results = {pattern: run_suite(tree_dir, pattern, a.bwrap) for pattern in a.suite}
            if any(tree_dir.rglob('__pycache__')):
                raise SystemExit('bytecode cache appeared in the disposable tree; results unreliable')
            rows.append({k: m[k] for k in ('id', 'operator', 'description')} | {'source_sha256': sha(m['source']), 'suites': results})
            if m['id'] == 'C-unmutated' and any(r['killed'] for r in results.values()):
                raise SystemExit(f'control failed: unmodified source killed {results}; check the sandbox and --out')
            if m['id'] == 'C-always-accept' and not all(r['killed'] for r in results.values()):
                raise SystemExit(f'control failed: always-accept survived {results}')
            status = ' '.join(f"{p}={'K' if r['killed'] else 'S'}" for p, r in results.items())
            print(m['id'], status, m['description'], flush=True)
    finally:
        target.write_text(source)
    names = [TARGET] + sorted({str(f.relative_to(ROOT)) for p in a.suite for f in (ROOT/'tests').glob(p)})
    files = {name: sha((ROOT/name).read_bytes()) for name in names}
    files.update({f'extra:{Path(e).name}': sha(Path(e).read_bytes()) for e in a.extra_test})
    files['harness'] = sha(Path(__file__).read_bytes())
    report = {'target': TARGET, 'functions': list(FUNCTIONS), 'suites': a.suite, 'sandbox': 'bwrap' if a.bwrap else None,
              'python': sys.version.split()[0], 'hashes': files, 'mutants': rows}
    (out/'kill-matrix.json').write_text(json.dumps(report, indent=1) + '\n')
    shutil.rmtree(tree_dir)


if __name__ == '__main__':
    main()
