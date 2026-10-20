"""Download public data only. Never import or execute downloaded programs."""
import argparse, concurrent.futures, hashlib, json, re, urllib.request, subprocess
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
COUNTS=[100,106,134,150,200,250,300,400,500,600,700,800]
PAGES={
 'packomania-csq.html':'https://packomania.com/csq/',
 'packomania-home.html':'https://www.packomania.com/',
 'packomania-pending.html':'https://www.packomania.com/pending-requests.html',
 'aletheia-findings.html':'https://www.projectaletheia.org/findings?view=canonical',
 'aletheia-datasets.html':'https://www.projectaletheia.org/datasets',
 'aletheia-research.html':'https://www.projectaletheia.org/research',
 'minmax47.html':'https://minmaxarena.com/en/problems/square-circle-packing/p01-n47-v1',
 'zerothesis.html':'https://zerothesis.com/challenges/circle-packing-square',
 'liang-readme.md':'https://raw.githubusercontent.com/jasonzliang/circle-packing-sota/main/README.md',
 'convexification.html':'https://arxiv.org/abs/2404.03091',
}

def acquire():
    requests=list(PAGES.items())
    for n in sorted({47}|{k for n in COUNTS for k in (n-1,n,n+1)}):
        requests.append((f'csq{n}.txt',f'https://packomania.com/csq/txt/csq{n}.txt'))
    def fetch(item):
        file,url=item
        raw=subprocess.check_output(['curl','-fLsS','--max-time','60',url])
        (ROOT/'sources'/file).write_bytes(raw)
        return {'path':'sources/'+file,'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),
                'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(fetch,requests))
    (ROOT/'sources/manifest.json').write_text(json.dumps(records,indent=2)+'\n')


def parse():
    soup=BeautifulSoup((ROOT/'sources/packomania-csq.html').read_bytes(),'html.parser')
    rows=[]
    for tr in soup.select('tr'):
        cells=tr.find_all('td',recursive=False)
        if len(cells)!=11: continue
        t=[c.get_text(' ',strip=True) for c in cells]
        if not t[0].isdigit(): continue
        n=int(t[0])
        if n not in COUNTS+[47]: continue
        ref=t[-1].strip('[]')
        credit=re.search(r'<tr><td align="right" valign="top">\['+ref+r'\].*?</tr>',
                         (ROOT/'sources/packomania-csq.html').read_text(),re.S)
        rows.append({'n':n,'published_radius':t[1], 'published_distance':t[2],
                     'contacts':t[5],'rattlers':t[6] or '0','reference':t[-1],
                     'proven_optimal_marked':bool(cells[1].find('strong') or cells[1].find('b')),
                     'by':BeautifulSoup(credit[0],'html.parser').get_text(' ',strip=True) if credit else t[-1],
                     'source':f'https://packomania.com/csq/csq{n}.html',
                     'coordinates_url':f'https://packomania.com/csq/txt/csq{n}.txt',
                     'updated':'2026-10-20','catalogue_updated':'2026-09-10',
                     'pending_uncertainty':'557 csq candidates in 401–1000; membership and values unavailable' if n>=401 else 'No matching range on 2026-10-17 pending list; not proof of no private competitor',
                     'independent_claim':'Aletheia candidate, no public numeric witness located' if n in [600,700,800] else None})
    (ROOT/'data/records.json').write_text(json.dumps(rows,indent=2)+'\n')
    # This independent witness is publicly rendered JSON, not code.
    soup=BeautifulSoup((ROOT/'sources/minmax47.html').read_bytes(),'html.parser')
    for p in soup.find_all('pre'):
        try: c=json.loads(p.get_text())
        except (ValueError,TypeError): continue
        if isinstance(c,dict) and len(c.get('centers',[]))==47 and 'radius' in c:
            (ROOT/'data/minmax47.json').write_text(json.dumps(c,indent=2)+'\n');break
    else: raise ValueError('MinMax public certificate not found')
    print(f'Parsed {len(rows)} Packomania rows and MinMax witness')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--parse-only',action='store_true');a=ap.parse_args()
    if not a.parse_only: acquire()
    parse()
