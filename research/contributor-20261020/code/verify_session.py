"""Offline exact verification plus integrity checks; standard library only."""
import hashlib,json,sys,time,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code/frozen'))
from verify import load_verify
from fractions import Fraction
from check_accounting import check_trial,gate
if not __debug__:raise RuntimeError("Run without -O: integrity assertions must be enabled")
started=time.monotonic();count=0;pairs=0
for p in sorted((ROOT/'certificates').rglob('*.json')):
    n=int(re.search(r'(?:^|-)n(\d+)(?:-|\.)',p.name).group(1)); result=load_verify(p,n);count+=1;pairs+=result['pairs_checked']
for p in (ROOT/'logs').glob('*/trials.jsonl'):
    config=json.loads((p.parent/'config.json').read_text());incumbents={};starts={}
    for line in p.read_text().splitlines():
        row=json.loads(line);cp=ROOT/row['certificate']
        assert hashlib.sha256(cp.read_bytes()).hexdigest()==row['certificate_sha256'],cp
        cert=json.loads(cp.read_text());ip=ROOT/row['input']
        assert hashlib.sha256(ip.read_bytes()).hexdigest()==cert['provenance']['input_sha256'],ip
        n=row['n']
        if n not in starts:
            original_path=ROOT/config.get('inputs','inputs')/f'n{n}.json'
            original=json.loads(original_path.read_text())
            assert hashlib.sha256(original_path.read_bytes()).hexdigest()==cert['provenance']['base_input_sha256']
            starts[n]=Fraction(original['radius_numerator'])/int(original['denominator']);incumbents[n]=starts[n]
        incumbents[n]=check_trial(row,cert,starts[n],incumbents[n])
    if (p.parent/'blocks.jsonl').exists():
        for line in (p.parent/'blocks.jsonl').read_text().splitlines():
            block=json.loads(line);assert Fraction(block['best_radius'])==incumbents[block['n']]
            retained=json.loads((ROOT/block['certificate']).read_text())
            assert Fraction(retained['radius_numerator'])/int(retained['denominator'])==incumbents[block['n']]
from decimal import Decimal
session=json.loads((ROOT/'session.json').read_text())
for name,h in session['input_sha256'].items():assert hashlib.sha256((ROOT/'inputs'/name).read_bytes()).hexdigest()==h,name
for config_path in (ROOT/'logs').glob('*/config.json'):
    config=json.loads(config_path.read_text())
    needed=['frozen/optimizer.py','frozen/certify.py','frozen/verify.py']
    needed+=['ipm_control.py','ipm_optimizer.py'] if config['phase']=='ipm-polish' else ['strong_polish.py' if config['phase']=='strong-polish' else 'polish_control.py'] if config['arm']=='polish-only' else ['run.py']
    if config['arm']=='targeted':needed+=['targeted.py']
    for name in needed:
        assert hashlib.sha256((ROOT/'code'/name).read_bytes()).hexdigest()==config['code_sha256'][name],(config_path,name)
for source in json.loads((ROOT/'sources/manifest.json').read_text()):
    assert hashlib.sha256((ROOT.parents[1]/source['path']).read_bytes()).hexdigest()==source['sha256'],source['path']
if (ROOT/'continuation-start.json').exists():
    for record in json.loads((ROOT/'continuation-start.json').read_text())['inputs']:
        assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256'],record['path']
        load_verify(ROOT/record['path'],record['n'])
if (ROOT/'strong-polish-start.json').exists():
    for record in json.loads((ROOT/'strong-polish-start.json').read_text())['inputs']:
        assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256'],record['path']
        load_verify(ROOT/record['path'],record['n'])
if (ROOT/'summary.json').exists():
    for row in json.loads((ROOT/'summary.json').read_text())['standings']:
        c=json.loads((ROOT/row['certificate']).read_text());r=Fraction(c['radius_numerator'])/int(c['denominator'])
        assert r==Fraction(row['retained_radius'])
        original=json.loads((ROOT/'inputs'/f'n{row['n']}.json').read_text());start=Fraction(original['radius_numerator'])/int(original['denominator'])
        assert r-start==Fraction(row['certified_gain'])
        assert bool(row['meaningful'])==(r-start>gate(start))
print(json.dumps({'valid':True,'certificates':count,'pair_checks':pairs,'seconds':time.monotonic()-started,'input_and_trial_hashes_checked':True}))
