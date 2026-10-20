"""Scientific SVG artifacts. Actual circle sizes; no exaggerated geometry."""
import datetime,html,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code/frozen'))
import numpy as np
from optimizer import from_certificate,graph
S=json.loads((ROOT/'summary.json').read_text())
START=datetime.datetime.fromisoformat(json.loads((ROOT/'session.json').read_text())['started_at'])
BG='#f5f3ed';INK='#152f37';TEAL='#167d8d';CORAL='#d34b3f';MUTED='#52666d'
def text(x,y,value,size=18,color=INK,extra=''):return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" {extra}>{html.escape(str(value))}</text>'
def begin(w,h):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="{w}" height="{h}" fill="{BG}"/>']
rows=[]
for p in (ROOT/'logs').glob('*/trials.jsonl'):rows.extend(json.loads(l) for l in p.read_text().splitlines())
rows.sort(key=lambda r:r['utc'])
out=begin(1200,780)
out+=[text(55,60,'Can the next contributor still improve the packing?',32),text(55,95,'A bounded local test from the previous pilot’s strongest certified constructions.',18,MUTED),text(55,135,'ADDITIONAL RADIUS  ·  parts per million (ppm)',15,MUTED)]
maxppm=max(1,max(r['gain_ppm'] for r in S['standings']))*1.1
for i,r in enumerate(S['standings']):
    y=180+45*i;w=max(0,r['gain_ppm']/maxppm*760)
    out+=[text(55,y+5,f"N={r['n']}",18),f'<rect x="155" y="{y-17}" width="760" height="27" fill="#dfe5df"/>',f'<rect x="155" y="{y-17}" width="{w:.3f}" height="27" fill="{TEAL}"/>',text(940,y+5,f"{r['gain_ppm']:.3f} ppm" if r['meaningful'] else 'No meaningful gain',17)]
out+=[text(55,430,'Best verified radius over the session',22),text(55,458,'Each line keeps the best result so far. Flat sections show no additional progress.',16,MUTED)]
chart=(95,490,1020,200);x0,y0,w,h=chart
maxminutes=max(1,max(((datetime.datetime.fromisoformat(r['utc'])-START).total_seconds()/60 for r in rows),default=1))
for frac in [0,.5,1]:
    y=y0+h-h*frac
    out+=[f'<line x1="{x0}" y1="{y}" x2="{x0+w}" y2="{y}" stroke="#c9d3cf"/>',text(20,y+5,f'{maxppm*frac:.1f}',14,MUTED)]
for r,color in zip([s for s in S['standings'] if s['meaningful']],[TEAL,CORAL,'#7364a5','#9b7510','#3f8846']):
    peak=0;pts=[(x0,y0+h)]
    for row in rows:
        if row['n']!=r['n']:continue
        gain=(float(row['radius'])/float(r['initial_radius'])-1)*1e6;peak=max(peak,gain)
        minute=(datetime.datetime.fromisoformat(row['utc'])-START).total_seconds()/60
        x=x0+minute/maxminutes*w
        pts.append((x,pts[-1][1]))
        pts.append((x,y0+h-peak/maxppm*h))
    pts.append((x0+w,pts[-1][1]))
    out.append('<polyline fill="none" stroke="'+color+'" stroke-width="3" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
    out.append(text(x0+w-100,pts[-1][1]-8,f"N={r['n']}",16,color))
for frac in [0,.25,.5,.75,1]:out.append(text(x0+w*frac-8,y0+h+27,f'{maxminutes*frac:.0f}m',14,MUTED))
out+=[text(55,755,'Exact feasibility checked. Improvements over this pilot are not established world records.',16,MUTED),'</svg>']
(ROOT/'images/progress.svg').write_text('\n'.join(out))
# Show the strongest non-polish discovery if available; otherwise the largest gain.
choices=[r for r in S['standings'] if r['meaningful'] and r['best_trial']['mode']!='polish']
r=max(choices or S['standings'],key=lambda s:s['gain_ppm']);n=r['n']
a=json.loads((ROOT/'inputs'/f'n{n}.json').read_text());b=json.loads((ROOT/r['certificate']).read_text())
def physical(c):return np.array(c['centers'],dtype=float)/int(c['denominator']),int(c['radius_numerator'])/int(c['denominator'])
pa,ra=physical(a);pb,rb=physical(b);ga=graph(from_certificate(a));gb=graph(from_certificate(b))
added={(i,j) for i,j in gb-ga if j<n};removed={(i,j) for i,j in ga-gb if j<n}
changed=set(k for e in added|removed for k in e)
if changed:
    k=max(changed,key=lambda k:np.linalg.norm(pa[k]-pb[k]));focus=(pa[k]+pb[k])/2
else:focus=np.array([.5,.5])
width=.22;focus=np.clip(focus,width/2,1-width/2);lo=focus-width/2
out=begin(1320,1140)
out+=[text(50,55,f'How do you fit {n} equal circles into a square?',32),text(50,88,'Move a few circles, release tight contacts, then check every pair exactly.',19,MUTED)]
def packing(p,r,x,y,size,edges=None,zoom=False,clipid='p'):
    arr=[];unit=width if zoom else 1;offset=lo if zoom else np.array([0,0]);scale=size/unit
    arr+=[f'<defs><clipPath id="{clipid}"><rect x="{x}" y="{y}" width="{size}" height="{size}"/></clipPath></defs>',f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="white" stroke="{INK}" stroke-width="1.5"/>',f'<g clip-path="url(#{clipid})">']
    for k,(cx,cy) in enumerate(p):
        px=x+(cx-offset[0])*scale;py=y+size-(cy-offset[1])*scale
        arr.append(f'<circle cx="{px:.6f}" cy="{py:.6f}" r="{r*scale:.6f}" fill="{TEAL}" fill-opacity=".23" stroke="{TEAL}" stroke-width=".65"/>')
    if edges:
        for i,j in edges:
            x1,y1=p[i]-offset;x2,y2=p[j]-offset
            arr.append(f'<line x1="{x+x1*scale:.6f}" y1="{y+size-y1*scale:.6f}" x2="{x+x2*scale:.6f}" y2="{y+size-y2*scale:.6f}" stroke="{CORAL}" stroke-width="2.2"/>')
    arr.append('</g>')
    if not zoom:arr.append(f'<rect x="{x+lo[0]*scale}" y="{y+size-(lo[1]+width)*scale}" width="{width*scale}" height="{width*scale}" fill="none" stroke="{CORAL}" stroke-width="2" stroke-dasharray="6 4"/>')
    return arr
out+=[text(50,135,'START: previous pilot',21),text(700,135,'AFTER: retained construction',21)]
out+=packing(pa,ra,50,155,570,clipid='full-a')+packing(pb,rb,700,155,570,clipid='full-b')
out+=[text(50,755,f'r = {r["initial_radius"]}',18),text(700,755,f'r = {r["retained_radius"]}',18),text(50,800,'Same region, enlarged',22),text(700,800,f'Radius gain: {r["gain_ppm"]:.3f} parts per million',23,TEAL)]
out+=packing(pa,ra,50,820,245,removed,True,'zoom-a')+packing(pb,rb,330,820,245,added,True,'zoom-b')
out+=[text(50,1090,'Before: released near-contacts',14,MUTED),text(330,1090,'After: added near-contacts',14,MUTED),text(700,845,'The radius increase is too small to see at full scale.',18,MUTED),text(700,878,'The rearrangement can be visible in a local close-up.',18,MUTED),text(700,920,'Geometry is shown at its actual proportions.',18),text(700,950,'Red lines indicate changed approximate contacts;',17,MUTED),text(700,978,'they are a visual guide, not the feasibility proof.',17,MUTED),text(700,1020,'The proof checks integer coordinates, every wall,',17,MUTED),text(700,1048,'and every circle pair. Novelty remains unresolved.',17,MUTED),text(50,1123,'Source constructions: Packomania. Local numerical refinement: Discovery@Home pilot. No optimality claim.',15,MUTED),'</svg>']
(ROOT/'images/demo.svg').write_text('\n'.join(out))
metrics={'n':n,'added_approximate_pair_contacts':len(added),'removed_approximate_pair_contacts':len(removed),'contact_relative_tolerance':2e-5,'max_center_displacement':float(np.max(np.linalg.norm(pa-pb,axis=1))),'median_center_displacement':float(np.median(np.linalg.norm(pa-pb,axis=1))),'radius_gain_ppm':r['gain_ppm'],'radius_gain_pixels_at_570px':(rb-ra)*570,'zoom_square_side':width,'disclaimer':'Labeled near-contact differences do not establish non-isomorphic contact topology; geometry is actual scale.'}
(ROOT/'visual-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics))
