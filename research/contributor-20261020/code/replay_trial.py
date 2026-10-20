"""Replay one saved start using recorded iteration budgets, not original wall cutoffs.

Exact output certificates, not floating point trajectories, are the portable proof.
"""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE/'frozen'))
import numpy as np
from scipy.optimize import minimize
from targeted import energy_gradient
from optimizer import relax,to_unit_circles
from certify import make_certificate,save,radius
ap=argparse.ArgumentParser();ap.add_argument('phase');ap.add_argument('n',type=int);ap.add_argument('attempt',type=int);ap.add_argument('--output',required=True);a=ap.parse_args()
rows=[json.loads(line) for line in (ROOT/'logs'/a.phase/'trials.jsonl').read_text().splitlines()]
row=next(r for r in rows if r['n']==a.n and r['attempt']==a.attempt)
p=np.array(json.loads((ROOT/row['input']).read_text())['points'])
if row['soft']:
    s=row['soft'];target=s['target']
    result=minimize(lambda x:energy_gradient(x,target),p.ravel(),jac=True,method='L-BFGS-B',bounds=[(0,1)]*(2*len(p)),
        options={'maxiter':max(1,s['iterations']),'maxcor':12,'ftol':1e-16,'gtol':1e-10,'maxls':30})
    p=result.x.reshape(-1,2)
p,stats=relax(p,max_steps=row['lp']['lp_steps'],seconds=120)
c=make_certificate(to_unit_circles(p),{'replay':row['certificate'],'iterations':row['lp']['lp_steps']});save(c,a.output)
print(json.dumps({'original_radius':row['radius'],'replay_radius':str(radius(c)),'absolute_delta':str(radius(c)-__import__('decimal').Decimal(row['radius'])),'lp':stats}))
