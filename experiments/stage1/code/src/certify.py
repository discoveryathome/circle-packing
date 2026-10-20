"""Construct rational witnesses by rounding centers, then shrinking radius exactly."""
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from math import isqrt
from pathlib import Path
import json
from verify import verify

SCALE = 10**15


def make_certificate(centers, provenance, scale=SCALE):
    with localcontext() as ctx:
        ctx.prec = 80
        points = [[int((Decimal(str(v))*scale).to_integral_value(rounding=ROUND_HALF_EVEN))
                   for v in p] for p in centers]
    wall = min(min(x,y,scale-x,scale-y) for x,y in points)
    pair = min(((x-u)**2+(y-v)**2 for i,(x,y) in enumerate(points)
                for u,v in points[:i]), default=scale*scale)
    r = min(wall, isqrt(pair)//2) if len(points)>1 else wall
    c = {'schema':'equal-circle-square/v1','n':len(points),'denominator':str(scale),
         'radius_numerator':str(r),'centers':[[str(x),str(y)] for x,y in points],
         'provenance':provenance}
    verify(c)
    return c


def radius(c):
    return Decimal(c['radius_numerator'])/Decimal(c['denominator'])


def save(c, path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(c,indent=2)+'\n')


def svg(c, path):
    verify(c)
    q = int(c['denominator'])
    r = int(c['radius_numerator'])/q
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.04 -0.09 1.08 1.14" width="720" height="760">',
           '<rect x="-0.04" y="-0.09" width="1.08" height="1.14" fill="#f6f4ed"/>',
           f'<text x="0" y="-0.045" font-size="0.022" font-family="monospace">N={c["n"]}  certified r={radius(c)}</text>',
           '<rect width="1" height="1" fill="white" stroke="#172b35" stroke-width="0.003"/>',
           '<g transform="translate(0,1) scale(1,-1)" fill="#6cbdaf" fill-opacity="0.65" stroke="#135c67" stroke-width="0.0008">']
    for x,y in c['centers']:
        out.append(f'<circle cx="{int(x)/q:.15f}" cy="{int(y)/q:.15f}" r="{r:.15f}"/>')
    out += ['</g></svg>']
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text('\n'.join(out)+'\n')
