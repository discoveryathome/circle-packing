"""Local protocol validation using the pinned upstream JSON schemas; no hub access."""
import argparse,json,subprocess,sys
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
def main(first_steps=False):
    for f,schema in [('discover.json','manifest'),('discover/frontier.json','frontier'),
                     ('discover/catalog.json','catalog')]:
        jsonschema.Draft202012Validator(json.loads((ROOT/f'sources/schemas/{schema}.schema.json').read_text()),
            format_checker=jsonschema.FormatChecker()).validate(json.loads((ROOT/f).read_text()))
    for package in sorted((ROOT/'research').glob('*/TASK.json')):
        jsonschema.Draft202012Validator(json.loads((ROOT/'sources/schemas/package-task.schema.json').read_text())).validate(json.loads(package.read_text()))
        for name in ['README.md','SOURCES.json','VERIFY.json']:
            if not (package.parent/name).exists():raise ValueError('incomplete result package: '+str(package.parent/name))
    cat=json.loads((ROOT/'discover/catalog.json').read_text())
    if sum(t['weight'] for t in cat['tracks'])!=100:raise ValueError('weights do not sum to 100')
    ids=[task['id'] for tr in cat['tracks'] for task in tr['tasks']]
    if len(set(ids))!=len(ids):raise ValueError('duplicate cards')
    manifest=json.loads((ROOT/'discover.json').read_text())
    for f in list(manifest['entry'].values())+[manifest['frontier'],manifest['catalog'],manifest['priority_log']]:
        if not (ROOT/f).exists():raise ValueError('missing '+f)
    if first_steps:
        for tr in cat['tracks']:
            for task in tr['tasks']:
                cmd=task['first_step']['command'][:]
                if cmd[0]=='python3':cmd[0]=sys.executable
                print('FIRST STEP',task['id'],flush=True)
                subprocess.run(cmd,cwd=ROOT,check=True)
    print('VALID: upstream schemas, weights, card IDs, entry paths. Pre-release contributions and expert-agent review open; scientific acceptance requires review.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['validate']);ap.add_argument('path',nargs='?',default='.')
    ap.add_argument('--first-steps',action='store_true');a=ap.parse_args();main(a.first_steps)
