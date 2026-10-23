"""Check policy-driven gallery generation without changing scientific inputs."""
import argparse
import hashlib
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = '978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a'
sys.path.insert(0, str(ROOT/'src'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def payload(text):
    start = text.index('const data=')+len('const data=')
    return text[start:text.index(';\n', start)]


def status(text):
    match = re.search(r'<span class="status">(.*?)</span>', text, re.S)
    if match is None:
        raise ValueError('missing participation-status element')
    return html.unescape(match.group(1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    baseline = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{BASE}:gallery/index.html']).decode()
    policy_raw = (ROOT/'PARTICIPATION.json').read_bytes()
    baseline_policy = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{BASE}:PARTICIPATION.json'])
    if policy_raw != baseline_policy:
        raise ValueError('authoritative participation policy was changed')
    policy = json.loads(policy_raw)
    spec = importlib.util.spec_from_file_location('gallery_generator', ROOT/'src/build_gallery.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected_payload = digest(payload(baseline).encode())
    fixtures, failures = [], []
    with tempfile.TemporaryDirectory(prefix='gallery-policy-', dir=ROOT.parent) as directory:
        fixture = Path(directory)
        (fixture/'gallery').mkdir()
        for name in ('certificates', 'research'):
            (fixture/name).symlink_to(ROOT/name, target_is_directory=True)
        shutil.copyfile(ROOT/'gallery/template.html', fixture/'gallery/template.html')
        module.ROOT = fixture
        for intake in ('open', 'closed', '<open & review>'):
            (fixture/'PARTICIPATION.json').write_text(json.dumps(dict(policy, intake=intake)))
            module.build()
            generated = (fixture/'gallery/index.html').read_text()
            rendered = status(generated)
            same_payload = digest(payload(generated).encode()) == expected_payload
            matched = rendered == 'Pre-release research preview · Contributor intake '+intake
            fixtures.append({'intake': intake, 'status': rendered, 'matches': matched,
                             'scientific_payload_unchanged': same_payload})
            if not matched or not same_payload:
                failures.append('generation fixture: '+intake)
    current = (ROOT/'gallery/index.html').read_text()
    expected = baseline.replace('Contributor intake closed', 'Contributor intake '+html.escape(policy['intake']))
    only_status = current == expected
    production_status = status(current) == 'Pre-release research preview · Contributor intake '+policy['intake']
    same_payload = digest(payload(current).encode()) == expected_payload
    if not production_status or not same_payload:
        failures.append('production status or scientific payload mismatch')
    result = {'status': 'author-checked generation audit; rendered checks are in the separate browser report', 'base_commit': BASE,
              'seed': 'c68557875f8ed1f9b2d61ce46a7dc42e', 'fixtures': fixtures,
              'policy_sha256': digest(policy_raw), 'policy_unchanged_from_base': True,
              'template_sha256': digest((ROOT/'gallery/template.html').read_bytes()),
              'generator_sha256': digest((ROOT/'src/build_gallery.py').read_bytes()),
              'index_sha256': digest(current.encode()), 'audit_sha256': digest(Path(__file__).read_bytes()),
              'scientific_payload_sha256': expected_payload,
              'displayed_counts': [row['n'] for row in json.loads(payload(current))],
              'production_status_matches_policy': production_status,
              'scientific_payload_unchanged': same_payload,
              'production_change_is_status_only': only_status, 'failures': failures,
              'not_checked': ['Real browser rendering, pointer mapping, linked zoom or narrow viewport behavior',
                              'External record standing, novelty, optimality or scientific acceptance']}
    rendered = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end='')
    if failures:
        raise ValueError('; '.join(failures))


if __name__ == '__main__':
    main()
