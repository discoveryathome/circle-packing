"""Diagnostic: can plain longer local optimization explain the apparent strategy gain?"""
import datetime,hashlib,json,os,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'code'
sys.path.insert(0,str(HERE/'frozen'))
from optimizer import from_certificate,to_unit_circles,relax
from certify import make_certificate,save,svg,radius
phase='long-polish';out=ROOT/'logs'/phase;out.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
(out/'config.json').write_text(json.dumps({'phase':phase,'arm':'polish-only','replicate':-1,'max_seconds_per_count':90,'max_steps':3000,'start':utc(),'code_sha256':{str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*.py')}},indent=2)+'\n')
for n in [500,800]:
    inp=ROOT/'inputs'/f'n{n}.json';initial=json.loads(inp.read_text());p=from_certificate(initial);start_radius=float(radius(initial))
    ip=ROOT/'inputs'/f'{phase}-n{n}-000.json';ip.write_text(json.dumps({'points':p.tolist(),'mode':'polish','attempt':0})+'\n')
    t=time.monotonic();cpu=time.process_time();p,stats=relax(p,max_steps=3000,seconds=90)
    c=make_certificate(to_unit_circles(p),{'experiment':phase,'arm':'polish-only','mode':'polish','attempt':0,'input_sha256':sha(ip),'base_input_sha256':sha(inp)})
    cp=ROOT/'certificates'/f'{phase}-n{n}-000.json';save(c,cp);r=float(radius(c));gate=max(1e-10,1e-8*start_radius)
    row={'phase':phase,'arm':'polish-only','replicate':-1,'n':n,'attempt':0,'mode':'polish','radius':str(radius(c)),'base_radius':str(radius(initial)),'gain_vs_session_start':r-start_radius,'gain_vs_incumbent':r-start_radius,'meaningful':r-start_radius>gate,'above_start_gate':r-start_radius>gate,'wall_seconds':time.monotonic()-t,'cpu_seconds':time.process_time()-cpu,'lp':stats,'soft':{},'basin_accepted':True,'certificate':str(cp.relative_to(ROOT)),'input':str(ip.relative_to(ROOT)),'certificate_sha256':sha(cp),'load_average':os.getloadavg(),'utc':utc()}
    with (out/'trials.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    best=c if radius(c)>radius(initial) else initial;dest=ROOT/'certificates'/phase/f'n{n}.json';save(best,dest);svg(best,ROOT/'images'/phase/f'n{n}.svg')
    block={'n':n,'attempts':1,'best_radius':str(radius(best)),'start_radius':str(radius(initial)),'wall_seconds':time.monotonic()-t,'cpu_seconds':time.process_time()-cpu,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'certificate':str(dest.relative_to(ROOT)),'end':utc()}
    with (out/'blocks.jsonl').open('a') as f:f.write(json.dumps(block)+'\n')
    print(json.dumps(row),flush=True);print('BLOCK '+json.dumps(block),flush=True)
