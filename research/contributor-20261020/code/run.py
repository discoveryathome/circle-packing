"""Bounded contributor experiment; every numerical proposal gets an exact witness."""
import argparse, datetime, hashlib, json, os, resource, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE/'frozen'))
import numpy as np
from optimizer import from_certificate, to_unit_circles, relax, perturb, score, graph
from certify import make_certificate, save, svg, radius

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--phase',required=True);ap.add_argument('--arm',choices=['original','targeted'],required=True)
    ap.add_argument('--counts',default='400,500,600,700,800');ap.add_argument('--seconds',type=float,default=60)
    ap.add_argument('--replicate',type=int,default=0);ap.add_argument('--inputs',default='inputs')
    args=ap.parse_args(); out=ROOT/'logs'/args.phase
    out.mkdir(parents=True,exist_ok=False)
    config=vars(args)|{'start':utc(),'code_sha256':{str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*.py')}}
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    for n in map(int,args.counts.split(',')):
        seed=int.from_bytes(hashlib.sha256(f'b8059878f07ecc1232784d188fffb6bc:{args.replicate}:{n}'.encode()).digest()[:16],'big')
        rng=np.random.default_rng(seed); inp=ROOT/args.inputs/f'n{n}.json'
        c=json.loads(inp.read_text()); base_r=float(radius(c)); best_c=c; best=from_certificate(c)
        current=best.copy(); block_t=time.monotonic();block_cpu=time.process_time(); attempt=0
        while time.monotonic()-block_t < args.seconds-1:
            t=time.monotonic(); cpu=time.process_time(); remain=args.seconds-(t-block_t)
            mode='polish' if attempt==0 else ['local','contact','basin'][(attempt-1)%3]
            if args.arm=='targeted':
                from targeted import propose, elastic
                p,mode=propose(best,current,rng,attempt)
            else:
                p=best.copy() if attempt==0 else perturb(current,rng,mode)
            tag=f'{args.phase}-n{n}-{attempt:03d}'
            start_path=ROOT/'inputs'/(tag+'.json')
            start_path.write_text(json.dumps({'points':p.tolist(),'mode':mode,'seed':str(seed),'attempt':attempt})+'\n')
            soft={}
            if args.arm=='targeted' and attempt>0:
                p,soft=elastic(p,score(best),seconds=min(5,remain*.35),rng=rng)
            p,stats=relax(p,max_steps=300,seconds=max(.05,min(18 if attempt==0 else 10,remain-(time.monotonic()-t)-.5)))
            cert=make_certificate(to_unit_circles(p),{'experiment':args.phase,'arm':args.arm,'mode':mode,'attempt':attempt,'seed':str(seed),'input_sha256':sha(start_path),'base_input_sha256':sha(inp)})
            cp=ROOT/'certificates'/(tag+'.json');save(cert,cp)
            r=float(radius(cert)); prev=float(radius(best_c)); gate=max(1e-10,1e-8*base_r)
            better=r>prev
            if better: best_c=cert;best=p.copy()
            # Basin walk accepts modest temporary deterioration; global best is immutable.
            accepted=better or r>=float(radius(best_c))*(1-2e-5) or rng.random()<.08
            current=p.copy() if accepted else best.copy()
            row={'phase':args.phase,'arm':args.arm,'replicate':args.replicate,'n':n,'attempt':attempt,'mode':mode,'radius':str(radius(cert)),'base_radius':str(radius(c)),
                 'gain_vs_session_start':r-base_r,'gain_vs_incumbent':r-prev,'meaningful':r-prev>gate,'above_start_gate':r-base_r>gate,
                 'wall_seconds':time.monotonic()-t,'cpu_seconds':time.process_time()-cpu,'lp':stats,'soft':soft,'basin_accepted':accepted,
                 'certificate':str(cp.relative_to(ROOT)),'input':str(start_path.relative_to(ROOT)),'certificate_sha256':sha(cp),'load_average':os.getloadavg(),'utc':utc()}
            with (out/'trials.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps({k:row[k] for k in ['phase','n','attempt','mode','radius','gain_vs_session_start','meaningful','wall_seconds']}),flush=True)
            attempt+=1
        dest=ROOT/'certificates'/args.phase/f'n{n}.json';save(best_c,dest);svg(best_c,ROOT/'images'/args.phase/f'n{n}.svg')
        summary={'n':n,'attempts':attempt,'best_radius':str(radius(best_c)),'start_radius':str(radius(c)),'wall_seconds':time.monotonic()-block_t,'cpu_seconds':time.process_time()-block_cpu,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'certificate':str(dest.relative_to(ROOT)),'end':utc()}
        with (out/'blocks.jsonl').open('a') as f:f.write(json.dumps(summary)+'\n')
        print('BLOCK '+json.dumps(summary),flush=True)
if __name__=='__main__':main()
