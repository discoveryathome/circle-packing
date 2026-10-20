"""Bounded, seeded search. Append-only trial evidence plus exact feasible witnesses."""
import argparse, hashlib, json, os, platform, sys, time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import numpy as np
import scipy
from certify import make_certificate, save, svg, radius
from optimizer import relax, score, to_unit_circles, from_certificate, perturb, neighboring, lattice, graph
from verify import verify

ROOT=Path(__file__).resolve().parents[1]

def load(path): return json.loads(Path(path).read_text())
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(r, published, cfg):
    baseline=Decimal(published);delta=r-baseline
    guard=Decimal(cfg['printed_radius_guard'])
    gate=max(Decimal(cfg['meaningful_absolute_gain']),baseline*Decimal(cfg['meaningful_relative_gain']))
    if delta>guard+gate: return 'historical-baseline-improvement_novelty-unresolved'
    if abs(delta)<=guard+gate:return 'numerical-tie'
    return 'below-baseline'


def run(out, cfg, continuation=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    records={r['n']:r for r in load(ROOT/'data/records.json')}
    if continuation:
        previous=load(Path(continuation)/'summary.json')
        # Rank positive gains first; if none, highest-radius relative gains select the strongest ties.
        ranked=sorted(previous['rows'],key=lambda r:Decimal(r['relative_gain']),reverse=True)
        selected=ranked[:cfg['continuation_counts']]
        counts=[r['n'] for r in selected]
        seeds=cfg['continuation_seeds'];modes=cfg['continuation_modes']
        trial_seconds=cfg['continuation_seconds_per_trial'];limit=cfg['continuation_wall_limit_seconds']
    else:
        counts=cfg['counts'];seeds=cfg['seeds'];modes=cfg['modes']
        trial_seconds=cfg['seconds_per_trial'];limit=cfg['stage1_wall_limit_seconds']
    metadata={'config':cfg,'config_sha256':hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest(),
              'counts':counts,'seeds':seeds,'started_at':datetime.now(timezone.utc).isoformat(),
              'platform':platform.platform(),'machine':platform.machine(),'python':sys.version,
              'numpy':np.__version__,'scipy':scipy.__version__,'continuation_of':str(continuation) if continuation else None,
              'source_hashes':{str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'src').glob('*.py')},
              'runtime_note':'Single solver worker; HiGHS threads=1; other machine load not controlled.'}
    save(metadata,out/'environment.json');save(cfg,out/'config.json')
    best={}; current={}; rows=[]; trial_id=0
    log=(out/'trials.jsonl').open('w')
    def trial(n, initial, mode, seed, seconds, parent):
        nonlocal trial_id
        before=graph(initial);t=time.monotonic()
        p,stats=relax(initial,cfg['max_steps'],min(seconds,max(.01,limit-(time.monotonic()-started))))
        c=make_certificate(to_unit_circles(p),{'kind':'local-search','mode':mode,'seed':seed,'parent':parent})
        verify(c,n)
        fname=f'trial-{trial_id:04d}-n{n}.json'
        save(c,out/'candidates'/fname)
        after=graph(p)
        entry={'trial':trial_id,'n':n,'mode':mode,'seed':seed,'parent':parent,
               'initial_distance':score(initial),'final_distance':score(p),
               'radius':str(radius(c)), 'classification':classify(radius(c),records[n]['published_radius'],cfg),
               'graph_edges_before':len(before),'graph_edges_after':len(after),
               'changed_edges':len(before^after),'certificate':f'candidates/{fname}',
               'certificate_sha256':digest(out/'candidates'/fname),**stats,
               'total_seconds':time.monotonic()-t}
        improved=radius(c)>radius(best[n])
        entry['improved_incumbent']=improved
        if improved:
            best[n]=c;save(c,out/'best'/f'n{n}.json')
        trial_id+=1
        return p,entry
    # All counts get a short baseline reproduction before interleaved search.
    for n in counts:
        parent=(Path(continuation)/'best'/f'n{n}.json') if continuation else ROOT/f'certificates/baseline/n{n}.json'
        c=load(parent); best[n]=c;current[n]=from_certificate(c)
        save(c,out/'best'/f'n{n}.json')
        if time.monotonic()-started<limit:
            current[n],entry=trial(n,current[n],'polish',0,cfg['polish_seconds'],str(parent.relative_to(ROOT)))
            entry['basin_accepted']=True;log.write(json.dumps(entry)+'\n');log.flush()
        print(f'polish N={n} r={radius(best[n])}',flush=True)
    # Fixed execution order: seeds, modes, counts; short windows spread compute across N.
    for seed in seeds:
        for mode in modes:
            for n in counts:
                if time.monotonic()-started>=limit:break
                rng=np.random.default_rng(np.random.SeedSequence([seed,n,modes.index(mode)]))
                parent=f'{out.name}/best/n{n}.json'
                if mode.startswith('neighbor'):
                    other=n+1 if mode=='neighbor-remove' else n-1
                    parent=f'certificates/baseline/n{other}.json'
                    p=neighboring(from_certificate(load(ROOT/parent)),n,rng)
                elif mode=='lattice':p=lattice(n,rng);parent='generated-staggered-lattice'
                else:
                    base=current[n] if mode=='basin' else from_certificate(best[n])
                    p=perturb(base,rng,mode)
                candidate,entry=trial(n,p,mode,seed,trial_seconds,parent)
                gain=score(candidate)-score(current[n]);temp=cfg['basin_temperature_distance']
                accept=gain>=0 or (mode=='basin' and rng.random()<np.exp(max(-700,gain/temp)))
                if accept:current[n]=candidate
                entry['basin_accepted']=bool(accept)
                log.write(json.dumps(entry)+'\n');log.flush()
            if time.monotonic()-started>=limit:break
        if time.monotonic()-started>=limit:break
    log.close()
    for n in counts:
        c=best[n];r=radius(c);pub=Decimal(records[n]['published_radius'])
        svg(c,out/'images'/f'n{n}.svg')
        row={'n':n,'published_radius':str(pub),'certified_radius':str(r),
             'absolute_gain':str(r-pub),'relative_gain':str((r-pub)/pub),
             'classification':classify(r,str(pub),cfg),'certificate':f'best/n{n}.json',
             'certificate_sha256':digest(out/'best'/f'n{n}.json')}
        if continuation:
            old=radius(load(Path(continuation)/'best'/f'n{n}.json'))
            row['continuation_gain']=str(r-old)
        rows.append(row)
    summary={'rows':rows,'trials':trial_id,'seconds':time.monotonic()-started,
             'time_limit':limit,'completed_schedule':trial_id==len(counts)*(1+len(seeds)*len(modes)),
             'meaningful_improvements':sum(r['classification'].startswith('historical') for r in rows)}
    save(summary,out/'summary.json');print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--config',default=str(ROOT/'experiments/config.json'))
    ap.add_argument('--continue-from');a=ap.parse_args()
    run(a.out,load(a.config),a.continue_from)
