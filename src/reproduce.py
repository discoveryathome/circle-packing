"""Offline check of record-table claims and evidence integrity; stdlib only."""
import argparse, hashlib, json, sys, time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from verify import load_verify

ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(all_trials=False):
    start=time.monotonic();count=0
    for source in load(ROOT/'sources/manifest.json'):
        if sha(ROOT/source['path'])!=source['sha256']:raise ValueError('source hash mismatch: '+source['path'])
    for path in sorted((ROOT/'certificates').glob('**/*.json')):
        load_verify(path);count+=1
    rows=load(ROOT/'data/frontier.json')
    for row in rows:
        report=load_verify(ROOT/row['certificate'],int(row['n']))
        if report['sha256']!=row['certificate_sha256']:raise ValueError('witness hash mismatch')
        if Fraction(report['radius_exact'])!=Fraction(row['certified_radius']):raise ValueError('value mismatch')
        if not (ROOT/row['image']).exists():raise ValueError('missing SVG')
    # Stored trial classifications are recomputed independently with exact rational comparisons.
    for stage in ['stage1','continuation']:
        directory=ROOT/'experiments'/stage
        cfg=load(directory/'config.json');summary=load(directory/'summary.json')
        env=load(directory/'environment.json')
        for name,expected_hash in env['source_hashes'].items():
            snapshot=directory/'code'/name
            if sha(snapshot)!=expected_hash:raise ValueError('experiment code snapshot mismatch: '+name)
        records={r['n']:r for r in load(ROOT/'data/records.json')}
        lines=(directory/'trials.jsonl').read_text().splitlines()
        if len(lines)!=summary['trials']:raise ValueError('trial count mismatch')
        for line in lines:
            tr=json.loads(line);path=directory/tr['certificate']
            if sha(path)!=tr['certificate_sha256']:raise ValueError('trial hash mismatch')
            c=load(path);r=Fraction(c['radius_numerator'])/int(c['denominator'])
            if r!=Fraction(tr['radius']):raise ValueError('trial radius mismatch')
            p=Fraction(records[tr['n']]['published_radius'])
            gate=Fraction(cfg['printed_radius_guard'])+max(Fraction(cfg['meaningful_absolute_gain']),p*Fraction(cfg['meaningful_relative_gain']))
            expected=('historical-baseline-improvement_novelty-unresolved' if r-p>gate else
                      'numerical-tie' if abs(r-p)<=gate else 'below-baseline')
            if tr['classification']!=expected:raise ValueError('classification mismatch')
            if all_trials:load_verify(path,tr['n']);count+=1
        for r in summary['rows']:
            cert=load(directory/r['certificate'])
            val=Fraction(cert['radius_numerator'])/int(cert['denominator'])
            if val!=Fraction(r['certified_radius']):raise ValueError('stage summary mismatch')
            load_verify(directory/r['certificate'],r['n'])
    print(json.dumps({'ok':True,'certificates_checked':count,'frontier_rows':len(rows),
                      'all_trials':all_trials,'seconds':round(time.monotonic()-start,3)}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--all-trials',action='store_true');a=ap.parse_args()
    main(a.all_trials)
