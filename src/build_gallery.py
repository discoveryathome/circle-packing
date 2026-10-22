"""Build a self-contained local explorer from exactly verified witnesses; no network."""
import json
from pathlib import Path
from packing_task import ROOT, read, starts, radius


def build():
    data = []
    for row in starts():
        old, new = read(ROOT/row['previous_certificate']), read(ROOT/row['certificate'])
        def layout(c):
            q = int(c['denominator'])
            return {'r': float(radius(c)), 'exact': str(radius(c)),
                    'points': [[int(x)/q, 1-int(y)/q] for x,y in c['centers']]}
        gain = radius(new)-radius(old)
        data.append({'n': row['n'], 'before': layout(old), 'after': layout(new),
                     'ppm': float(gain/radius(old)*1_000_000), 'gain': str(gain),
                     'certificate': '../'+row['certificate'], 'previous': '../'+row['previous_certificate'],
                     'sha256': row['sha256'], 'credit': row['construction_credit'], 'source': row['source']})
    template = (ROOT/'gallery/template.html').read_text()
    payload = json.dumps(data, separators=(',', ':')).replace('<', '\\u003c')
    (ROOT/'gallery/index.html').write_text(template.replace('/*PACKING_DATA*/[]', payload))
    print(f'Built gallery/index.html from {len(data)} verified pairs; no external scripts or fonts.')


if __name__ == '__main__':
    build()
