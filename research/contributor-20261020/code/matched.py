"""Precommitted interleaved order for the held-out comparison."""
import datetime,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
schedule=[]
for replicate,counts in [(101,[400,500,600,700,800]),(102,[800,700,600,500,400])]:
    for index,n in enumerate(counts):
        arms=['original','targeted'] if (index+replicate)%2 else ['targeted','original']
        for arm in arms:schedule.append({'phase':f'heldout-{replicate}-{n}-{arm}','arm':arm,'n':n,'replicate':replicate,'seconds':45})
(ROOT/'matched-schedule.json').write_text(json.dumps(schedule,indent=2)+'\n')
for row in schedule:
    print(datetime.datetime.now(datetime.timezone.utc).isoformat(),row,flush=True)
    with (ROOT/'logs'/(row['phase']+'.stdout')).open('w') as f:
        subprocess.run([sys.executable,str(ROOT/'code/run.py'),'--phase',row['phase'],'--arm',row['arm'],'--counts',str(row['n']),'--seconds',str(row['seconds']),'--replicate',str(row['replicate'])],stdout=f,stderr=subprocess.STDOUT,check=True)
