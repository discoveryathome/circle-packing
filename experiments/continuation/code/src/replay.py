"""Replay one trial's initialization and recorded LP work, within a numerical gate.

Prior final states are reconstructed from exact certificates; their <=1e-15 rounding
can change a local path. This is a numerical reproduction check, not bitwise replay.
"""
import argparse,json,time
from decimal import Decimal
from pathlib import Path
import numpy as np
from optimizer import from_certificate, neighboring, lattice, perturb, relax, to_unit_circles
from certify import make_certificate,radius,save
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())

def replay(stage, trial_id, seconds, out):
    stage=Path(stage).resolve();env=load(stage/'environment.json');cfg=env['config']
    cont=bool(env['continuation_of']);modes=cfg['continuation_modes'] if cont else cfg['modes']
    previous=(ROOT/'experiments/stage1') if cont else None
    best={};current={}
    for n in env['counts']:
        c=load(previous/'best'/f'n{n}.json') if cont else load(ROOT/f'certificates/baseline/n{n}.json')
        best[n]=c;current[n]=from_certificate(c)
    for line in (stage/'trials.jsonl').read_text().splitlines():
        t=json.loads(line);n=t['n'];mode=t['mode']
        if t['trial']==trial_id:
            if mode=='polish':initial=current[n]
            else:
                rng=np.random.default_rng(np.random.SeedSequence([t['seed'],n,modes.index(mode)]))
                if mode.startswith('neighbor'):
                    other=n+1 if mode=='neighbor-remove' else n-1
                    initial=neighboring(from_certificate(load(ROOT/f'certificates/baseline/n{other}.json')),n,rng)
                elif mode=='lattice':initial=lattice(n,rng)
                else:initial=perturb(current[n] if mode=='basin' else from_certificate(best[n]),rng,mode)
            p,stats=relax(initial,max_steps=t['lp_steps'],seconds=seconds)
            c=make_certificate(to_unit_circles(p),{'kind':'replay','stage':stage.name,'trial':trial_id})
            difference=radius(c)-Decimal(t['radius'])
            gate=max(Decimal(cfg['meaningful_absolute_gain']),Decimal(t['radius'])*Decimal(cfg['meaningful_relative_gain']))
            report={'trial':trial_id,'n':n,'original_radius':t['radius'],'replayed_radius':str(radius(c)),
                    'difference':str(difference),'within_practical_gate':abs(difference)<=gate,**stats,
                    'limitation':'Prior states reconstructed from rounded certificates; not bitwise reproduction.'}
            save({'report':report,'certificate':c},out);print(json.dumps(report,indent=2));return
        c=load(stage/t['certificate'])
        if t['improved_incumbent']:best[n]=c
        if t['basin_accepted']:current[n]=from_certificate(c)
    raise ValueError('trial not found')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--trial',type=int,required=True)
    ap.add_argument('--seconds',type=float,default=20);ap.add_argument('--out',required=True);a=ap.parse_args()
    replay(a.stage,a.trial,a.seconds,a.out)
