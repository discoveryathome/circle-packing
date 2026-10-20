"""Offline exact verification plus integrity checks; standard library only."""
import hashlib,json,sys,time,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code/frozen'))
from verify import load_verify
start=time.monotonic();count=0;pairs=0
for p in sorted((ROOT/'certificates').rglob('*.json')):
    n=int(re.search(r'(?:^|-)n(\d+)(?:-|\.)',p.name).group(1)); result=load_verify(p,n);count+=1;pairs+=result['pairs_checked']
for p in (ROOT/'logs').glob('*/trials.jsonl'):
    for line in p.read_text().splitlines():
        row=json.loads(line);cp=ROOT/row['certificate']
        assert hashlib.sha256(cp.read_bytes()).hexdigest()==row['certificate_sha256'],cp
        cert=json.loads(cp.read_text());ip=ROOT/row['input']
        assert hashlib.sha256(ip.read_bytes()).hexdigest()==cert['provenance']['input_sha256'],ip
        assert cert['n']==row['n']
        from decimal import Decimal
        assert Decimal(cert['radius_numerator'])/Decimal(cert['denominator'])==Decimal(row['radius'])
from decimal import Decimal
session=json.loads((ROOT/'session.json').read_text())
for name,h in session['input_sha256'].items():assert hashlib.sha256((ROOT/'inputs'/name).read_bytes()).hexdigest()==h,name
print(json.dumps({'valid':True,'certificates':count,'pair_checks':pairs,'seconds':time.monotonic()-start,'input_and_trial_hashes_checked':True}))
