"""Run diagnostic and next-contributor blocks after the matched comparison."""
import datetime,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def run(script,args,log):
    print(utc(),script,args,flush=True)
    with (ROOT/'logs'/log).open('w') as f:subprocess.run([sys.executable,str(ROOT/'code'/script),*args],stdout=f,stderr=subprocess.STDOUT,check=True)
deadline=time.monotonic()+1800
while not (ROOT/'certificates/heldout-102-400-original/n400.json').exists():
    if time.monotonic()>deadline:raise RuntimeError('matched comparison incomplete')
    time.sleep(2)
run('polish_control.py',[],'long-polish.stdout')
run('analyze.py',[],'before-continuation-analysis.txt')
inputs=ROOT/'inputs/continuation-start';inputs.mkdir(exist_ok=False)
summary=json.loads((ROOT/'summary.json').read_text());manifest={'frozen_at':utc(),'selection':'N=500/800 were successful in exploration; N=700 added after held-out gain. Strongest observed witnesses across completed phases, including long polish','inputs':[]}
for n in [500,700,800]:
    source=ROOT/'certificates/best'/f'n{n}.json';dest=inputs/f'n{n}.json';shutil.copy2(source,dest)
    manifest['inputs'].append({'n':n,'path':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'standing':next(r for r in summary['standings'] if r['n']==n)})
(ROOT/'continuation-start.json').write_text(json.dumps(manifest,indent=2)+'\n')
schedule=[]
for replicate,counts in [(201,[500,800]),(202,[800,500])]:
    for i,n in enumerate(counts):
        arms=['original','targeted'] if (i+replicate)%2 else ['targeted','original']
        for arm in arms:schedule.append({'phase':f'continuation-{replicate}-{n}-{arm}','arm':arm,'n':n,'replicate':replicate,'seconds':60})
schedule += [{'phase':f'continuation-{replicate}-700-{arm}','arm':arm,'n':700,'replicate':replicate,'seconds':60} for replicate,arms in [(203,['targeted','original']),(204,['original','targeted'])] for arm in arms]
(ROOT/'continuation-schedule.json').write_text(json.dumps(schedule,indent=2)+'\n')
for row in schedule:run('run.py',['--phase',row['phase'],'--arm',row['arm'],'--counts',str(row['n']),'--seconds',str(row['seconds']),'--replicate',str(row['replicate']),'--inputs','inputs/continuation-start'],row['phase']+'.stdout')
run('run.py',['--phase','aa-original-repeat','--arm','original','--counts','500','--seconds','60','--replicate','0'],'aa-original-repeat.stdout')
(ROOT/'search-complete.json').write_text(json.dumps({'ended_at':utc()},indent=2)+'\n')
print('Search schedule complete',utc(),flush=True)
