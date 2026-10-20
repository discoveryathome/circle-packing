"""One final long-call diagnostic, queued after all short-call comparisons."""
import datetime,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
deadline=time.monotonic()+1200
while not (ROOT/'search-complete.json').exists():
    if time.monotonic()>deadline:raise RuntimeError('short-call schedule incomplete')
    time.sleep(2)
with (ROOT/'logs/before-strong-polish-analysis.txt').open('w') as f:subprocess.run([sys.executable,str(ROOT/'code/analyze.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
folder=ROOT/'inputs/strong-polish-start';folder.mkdir(exist_ok=False);records=[]
for n in [700,800]:
    p=folder/f'n{n}.json';shutil.copy2(ROOT/'certificates/best'/p.name,p)
    records.append({'n':n,'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'strong-polish-start.json').write_text(json.dumps({'frozen_at':utc(),'inputs':records},indent=2)+'\n')
with (ROOT/'logs/strong-polish.stdout').open('w') as f:subprocess.run([sys.executable,str(ROOT/'code/strong_polish.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
(ROOT/'all-search-complete.json').write_text(json.dumps({'ended_at':utc()},indent=2)+'\n')
print('All numerical work complete',utc(),flush=True)
