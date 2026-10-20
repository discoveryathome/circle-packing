"""Derive tables from raw logs; never infer novelty from a radius difference."""
import datetime,json,math,sys
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'code/frozen'))
from certify import radius,save,svg
D=Decimal
rows=[];blocks=[]
for p in sorted((ROOT/'logs').glob('*/trials.jsonl')):rows.extend(json.loads(line) for line in p.read_text().splitlines())
for p in sorted((ROOT/'logs').glob('*/blocks.jsonl')):
    config=json.loads((p.parent/'config.json').read_text())
    blocks.extend(json.loads(line)|{'phase':config['phase'],'arm':config['arm'],'replicate':config['replicate']} for line in p.read_text().splitlines())
rows.sort(key=lambda r:r['utc']);records={r['n']:r for r in json.loads((PROJECT/'data/records.json').read_text())}
standings=[]
for n in [400,500,600,700,800]:
    initial=json.loads((ROOT/'inputs'/f'n{n}.json').read_text());start=radius(initial);gate=max(D('1e-10'),D('1e-8')*start)
    eligible=[r for r in rows if r['n']==n];best=max(eligible,key=lambda r:D(r['radius']),default=None)
    meaningful=best is not None and D(best['radius'])-start>gate
    # Preserve the prior witness when the only numerical change is below the gate.
    c=json.loads((ROOT/best['certificate']).read_text()) if meaningful else initial
    path=ROOT/'certificates/best'/f'n{n}.json';save(c,path);svg(c,ROOT/'images/best'/f'n{n}.svg')
    final=radius(c);pub=D(records[n]['published_radius'])
    standings.append({'n':n,'initial_radius':str(start),'best_observed_radius':best['radius'] if best else str(start),'retained_radius':str(final),'certified_gain':str(final-start),'gain_ppm':float((final/start-1)*D(10**6)),'meaningful':meaningful,'gate':str(gate),'published_radius':str(pub),'gain_vs_published':str(final-pub),'published_gate_pass':final-pub>D('1e-12')+max(D('1e-10'),D('1e-8')*pub),'source':records[n]['source'],'original_construction_by':records[n]['by'],'best_trial':None if not meaningful else best,'certificate':str(path.relative_to(ROOT)),'image':f'images/best/n{n}.svg','density_gain':float(D(n)*D(str(math.pi))*(final*final-start*start))})
matched=[]
for replicate in [101,102]:
    for n in [400,500,600,700,800]:
        byarm={b['arm']:b for b in blocks if b['replicate']==replicate and b['n']==n and b['phase'].startswith('heldout-')}
        if len(byarm)!=2:continue
        delta=D(byarm['targeted']['best_radius'])-D(byarm['original']['best_radius']);gate=max(D('1e-10'),D('1e-8')*D(byarm['original']['start_radius']))
        matched.append({'replicate':replicate,'n':n,'targeted_minus_original':str(delta),'winner':'targeted' if delta>gate else 'original' if delta < -gate else 'tie','arms':byarm})
mode_stats=[]
for stage in ['exploration','heldout','continuation']:
    for arm in ['original','targeted']:
        group=[r for r in rows if r['phase'].startswith(stage) and r['arm']==arm]
        if not group:continue
        mode_stats.append({'stage':stage,'arm':arm,'trials':len(group),'meaningful_within_block_events':sum(r['meaningful'] for r in group),'above_block_start_trials':sum(r['above_start_gate'] for r in group),'cpu_seconds':sum(r['cpu_seconds'] for r in group),'wall_seconds':sum(r['wall_seconds'] for r in group),'lp_steps':sum(r['lp']['lp_steps'] for r in group),'lp_failure_trials':sum(r['lp']['lp_failures']>0 for r in group),'recovered_start_within_gate':sum(D(r['radius'])>=D(r['base_radius'])-max(D('1e-10'),D('1e-8')*D(r['base_radius'])) for r in group if r['mode']!='polish'),'nonpolish_trials':sum(r['mode']!='polish' for r in group)})
summary={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'trials':len(rows),'completed_blocks':len(blocks),'worker_wall_seconds':sum(b['wall_seconds'] for b in blocks),'worker_cpu_seconds':sum(b['cpu_seconds'] for b in blocks),'peak_worker_rss_bytes':max((b['peak_rss_bytes'] for b in blocks),default=0),'standings':standings,'matched':matched,'mode_stats':mode_stats,'blocks':blocks,'last_trial_at':None if not rows else rows[-1]['utc']}
(ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['# Certified results from this contributor session','','All radii describe identical circles inside the unit square. A retained improvement clears the practical gate against the **previous pilot**, not merely the printed catalogue. No new-record priority is established.','','| N | Previous pilot radius | Retained radius | Additional radius | Relative gain (ppm) | Evidence |','|---:|---:|---:|---:|---:|---|']
for r in standings:lines.append(f"|{r['n']}|{r['initial_radius']}|{r['retained_radius']}|{r['certified_gain']}|{r['gain_ppm']:.6f}|[witness]({r['certificate']}) · [SVG]({r['image']})|")
lines+=['','## External comparison','','The source catalogue and pending claims are distinct. See [source recheck](SOURCE_UPDATE.md).','','| N | Printed Packomania radius | Retained minus printed | Original construction credit | Standing |','|---:|---:|---:|---|---|']
for r in standings:lines.append(f"|{r['n']}|[{r['published_radius']}]({r['source']})|{r['gain_vs_published']}|{r['original_construction_by']}|{'Published-baseline gain; novelty unresolved' if r['published_gate_pass'] else 'Numerical tie'}|")
lines+=['','N=600 and 700 may retain earlier catalogue gains without making additional progress in this session. Raw smaller positive differences are preserved in summary.json and are not called meaningful gains.','']
(ROOT/'RESULTS.md').write_text('\n'.join(lines))
print(json.dumps({k:summary[k] for k in ['trials','completed_blocks','worker_wall_seconds','worker_cpu_seconds','peak_worker_rss_bytes']}))
for r in standings:print(r['n'],r['retained_radius'],r['certified_gain'],r['gain_ppm'])
