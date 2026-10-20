import json
from decimal import Decimal
from pathlib import Path
from certify import make_certificate, save, svg, radius
from verify import verify

ROOT=Path(__file__).resolve().parents[1]


def source_points(n):
    lines=(ROOT/f'sources/csq{n}.txt').read_text().splitlines()
    rows=[line.split() for line in lines if line.strip() and not line.lstrip().startswith('#')]
    if len(rows)!=n or any(len(p)!=4 for p in rows): raise ValueError('source format/count')
    if [int(p[0]) for p in rows]!=list(range(1,n+1)): raise ValueError('source indices')
    if len({p[3] for p in rows})!=1: raise ValueError('unequal source radii')
    return [[str(Decimal(p[1])+Decimal('.5')),str(Decimal(p[2])+Decimal('.5'))] for p in rows],rows[0][3]


def run():
    reports=[]
    for path in sorted((ROOT/'sources').glob('csq*.txt')):
        n=int(path.stem[3:]);points,claimed=source_points(n)
        c=make_certificate(points,{'source':f'sources/csq{n}.txt','kind':'published-coordinate-repair'})
        raw=dict(c); raw['radius_numerator']=str(int(Decimal(claimed)*int(c['denominator'])))
        try: verify(raw);raw_ok=True;failure=None
        except ValueError as e:raw_ok=False;failure=str(e)
        save(c,ROOT/f'certificates/baseline/n{n}.json')
        svg(c,ROOT/f'images/baseline/n{n}.svg')
        reports.append({'n':n,'published_radius':claimed,'raw_decimal_feasible':raw_ok,
                        'raw_failure':failure,'certified_radius':str(radius(c)),
                        'radius_reduction':str(Decimal(claimed)-radius(c)),
                        'certificate':f'certificates/baseline/n{n}.json'})
    m=json.loads((ROOT/'data/minmax47.json').read_text())
    c=make_certificate(m['centers'],{'source':'https://minmaxarena.com/en/problems/square-circle-packing/p01-n47-v1','kind':'independent-AI-construction'})
    c['radius_numerator']=str(int(Decimal(m['radius'])*int(c['denominator'])))
    verify(c,47);save(c,ROOT/'certificates/external/minmax47.json');svg(c,ROOT/'images/external/minmax47.svg')
    (ROOT/'experiments/baseline-audit.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(json.dumps({'baselines_certified':len(reports),'raw_feasible':sum(p['raw_decimal_feasible'] for p in reports),
                      'max_shrink':str(max(Decimal(p['radius_reduction']) for p in reports)),
                      'minmax47':'passes exactly at '+m['radius']}))

if __name__=='__main__':run()
