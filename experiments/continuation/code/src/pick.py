"""Own seeded local picker. Never gives permission to launch donor sessions."""
import argparse,hashlib,json,secrets
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--seed',default=None);a=ap.parse_args()
seed=a.seed or secrets.token_hex(16)
if len(seed)!=32 or any(c not in '0123456789abcdef' for c in seed):raise SystemExit('seed: 32 lowercase hex digits')
cat=json.loads((ROOT/'discover/catalog.json').read_text())
def draw(label):return int.from_bytes(hashlib.sha256((seed+':'+label).encode()).digest()[:8],'big')
x=draw('track')%100
for t in cat['tracks']:
    if x<t['weight']:break
    x-=t['weight']
card=t['tasks'][draw('card')%len(t['tasks'])]
print(json.dumps({'seed':seed,'track':t['id'],'task':card['id'],'first_step':card['first_step'],
                  'intake':'paused: local proposal, no agreed maintainer',
                  'overlap':'Check discover/ledger.jsonl and HANDOFF.md; no remote board exists.'},indent=2))
