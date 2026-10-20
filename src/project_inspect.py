import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('what',choices=['audit','neighbors','summary']);a=ap.parse_args()
if a.what=='summary':print((ROOT/'experiments/analysis.json').read_text())
elif a.what=='neighbors':
    cfg=json.loads((ROOT/'experiments/config.json').read_text())
    for n in cfg['counts']:
        for k in [n-1,n+1]:
            if not (ROOT/f'certificates/baseline/n{k}.json').exists():raise ValueError(f'missing neighbor {k}')
    print('24 neighboring-count witnesses present; validate before search. No new experiment performed.')
else:
    rows=json.loads((ROOT/'data/frontier.json').read_text())
    print(json.dumps({'targets':len(rows),'baseline_improvements':[r['n'] for r in rows if r['classification'].startswith('published')],
                      'externally_accepted_new_records':0,'pending_claim_counts':[600,700,800],
                      'pending_queue_source':'sources/packomania-pending.html',
                      'current_comparison':'data/frontier.json','historical_comparison':'data/historical.json',
                      'required_next_evidence':'Accessible pending witnesses/priority disposition; do not infer novelty from catalogue alone'},indent=2))
