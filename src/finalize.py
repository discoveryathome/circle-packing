"""Build local tables and reporting artifacts from completed experiment evidence."""
import collections, hashlib, json, shutil
from decimal import Decimal as D
from pathlib import Path
from certify import radius, save, svg
from verify import load_verify
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    stages=[ROOT/'experiments/stage1',ROOT/'experiments/continuation']
    summaries=[load(p/'summary.json') for p in stages]
    configs=load(ROOT/'experiments/config.json');base=load(ROOT/'data/records.json')
    historical={r['n']:r for r in load(ROOT/'data/historical.json')}
    audit=load(ROOT/'experiments/baseline-audit.json')
    rows=[]
    for rec in base:
        n=rec['n']
        if n not in configs['counts']:continue
        choices=[ROOT/f'certificates/baseline/n{n}.json']+[p/f'best/n{n}.json' for p in stages if (p/f'best/n{n}.json').exists()]
        origin=max(choices,key=lambda p:radius(load(p)));c=load(origin)
        dest=ROOT/f'certificates/frontier/n{n}.json';save(c,dest)
        svg(c,ROOT/f'images/frontier/n{n}.svg')
        r=radius(c);pub=D(rec['published_radius']);gate=D(configs['printed_radius_guard'])+max(D(configs['meaningful_absolute_gain']),pub*D(configs['meaningful_relative_gain']))
        meaningful=r-pub>gate
        row={**rec,'certified_radius':str(r),'delta_vs_published':str(r-pub),
             'classification':'published-baseline improvement; novelty unresolved' if meaningful else 'numerical tie; baseline reproduced',
             'novel_record':False,'witness_origin':str(origin.relative_to(ROOT)),
             'certificate':str(dest.relative_to(ROOT)),'certificate_sha256':sha(dest),
             'image':f'images/frontier/n{n}.svg','verification':'exact feasible lower bound; author-checked',
             'local_work_credit':'Pilot refinement from imported construction; not a priority claim'}
        if n in historical:
            h=historical[n];row['historical_radius_upper']=h['historical_radius_upper']
            row['delta_vs_historical_upper']=str(r-D(h['historical_radius_upper']))
            row['historical_source']=h['source']
        rows.append(row)
    save(rows,ROOT/'data/frontier.json')
    # An independent run checker can recompute each row, not just read its score.
    table=['# Source-backed record table','',
           'All radii refer to equal circles inside a unit square. Published values are rounded source numbers; local values are exact feasible decimal rationals. No row claims external acceptance or optimality. Source snapshots: 20 October 2026.','',
           '| N | Published radius | Certified local radius | Δ vs published | Disposition | Witness / SVG |',
           '|---:|---:|---:|---:|---|---|']
    for r in rows:
        table.append(f'|{r["n"]}|[{r["published_radius"]}]({r["source"]})|{r["certified_radius"]}|{D(r["delta_vs_published"]):+.3E}|{r["classification"]}|[JSON]({r["certificate"]}) · [SVG]({r["image"]})|')
    table+=['','N=500–800 overlap the range of 557 pending `csq` submissions. N=600,700,800 also have Aletheia pending claims without accessible numerical witnesses in this audit. Other rows have no matching range in the frozen pending list, which does not establish novelty. Full attribution, source dates and uncertainty are in `data/frontier.json`.','',
            '## Comparison with pre-2023 history','',
            'Lai et al. Tables 4/6 report earlier best container side lengths for unit-radius circles. Inverting their conservatively guarded printed values gives the radius comparison below. Gains already present in the published source are rediscoveries, not new records.','',
            '| N | Historical L | Guarded historical r upper | Local r minus upper | Interpretation |','|---:|---:|---:|---:|---|']
    for r in rows:
        n=r['n']
        if n not in historical:continue
        h=historical[n]
        interpretation='Known historical advance already in Packomania' if n in [250,400] else 'Tie/precision-scale difference; no novelty inference'
        table.append(f'|{n}|{h["historical_side_length"]}|{D(h["historical_radius_upper"]):.15f}|{D(r["delta_vs_historical_upper"]):+.3E}|{interpretation}|')
    table+=['','Source: [Lai et al., author manuscript](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalJOC2023.pdf), Tables 4 and 6; historical centers were not imported. [Audit and guards](AUDIT.md).']
    (ROOT/'RECORDS.md').write_text('\n'.join(table)+'\n')
    gallery=['# Certified construction gallery','', 'Every displayed packing has passed the exact checker. These are local feasibility acceptances, not external record acceptances. [Record table](../RECORDS.md).','']
    for r in rows:
        gallery += [f'## N={r["n"]} — r={r["certified_radius"]}', '',f'![N={r["n"]} certified packing](frontier/n{r["n"]}.svg)','']
    gallery+=['Baseline and neighbor SVGs are under `baseline/`; the independently rechecked N=47 AI control is under `external/`. Every stage winner also has an SVG in its experiment directory. Other trial witnesses are archived candidates, not accepted frontier constructions.']
    (ROOT/'images/GALLERY.md').write_text('\n'.join(gallery)+'\n')
    frontier={'schema':'discover-frontier/v0','statement':'Exact feasible lower bounds for 12 selected equal-circle square packings. Two published-baseline improvements are novelty-unresolved; no new-record or global-optimality claim.',
              'status':'Local proposal; donor intake deferred; no agreed maintainer', 'evidence_level':['author-checked'], 'claim_kind':['exact'],
              'scope':'N in {100,106,134,150,200,250,300,400,500,600,700,800}; square [0,1]^2, identical radii, tangency allowed.',
              'assumptions':[{'id':'novelty','statement':'Pending submissions and Aletheia numerical witnesses remain unreconciled. This does not affect the exact feasibility claim.','status':'open','link':'AUDIT.md'}],
              'sources':['https://packomania.com/csq/','https://www.packomania.com/pending-requests.html','AUDIT.md'],
              'table':{'path':'data/frontier.json','format':'json','key':['n'],'value':'certified_radius','direction':'higher-is-better','object':'certificate',
                       'check_row':['python3','src/verify.py','{certificate}','--n','{n}'],'check_row_minutes':1,'by':'by','source':'source','updated':'updated'},
              'artifacts':[{'path':r['certificate'],'sha256':r['certificate_sha256'],'role':'feasible packing'} for r in rows],
              'reproduce':'python3 src/reproduce.py','reproduce_full':'python3 src/reproduce.py --all-trials','reproduce_minutes':2,
              'prerequisites':['Python 3.10+ standard library; no network for verification'],'review':'discover/review.md','updated_on':'2026-10-20'}
    save(frontier,ROOT/'discover/frontier.json')
    trials=[[json.loads(s) for s in (p/'trials.jsonl').read_text().splitlines()] for p in stages]
    comparisons=[]
    for r in summaries[1]['rows']:
        old=next(x for x in summaries[0]['rows'] if x['n']==r['n']);gain=D(r['certified_radius'])-D(old['certified_radius'])
        gate=max(D(configs['meaningful_absolute_gain']),D(old['certified_radius'])*D(configs['meaningful_relative_gain']))
        comparisons.append({'n':r['n'],'stage1':old['certified_radius'],'continuation':r['certified_radius'],'gain':str(gain),'meaningful':gain>gate})
    save({'stages':summaries,'continuation_comparison':comparisons},ROOT/'experiments/analysis.json')
    report=['# Pilot result and recommendation','',
            '**Defer broad donated-session launch.** The pilot demonstrates cheap, rigorous verification and some numerical headroom over a frozen catalogue. It does not establish unclaimed record headroom: the successful counts overlap independent pending claims, and no maintainer has agreed to review contributions. A focused local follow-up is justified; a public record-hunting launcher is premature.','',
            '## Observed results','',
            f'- {len(configs["counts"])} target counts, two discovery seeds, six search modes, plus unperturbed polish: {summaries[0]["trials"]} trials in {summaries[0]["seconds"]:.1f} seconds.',
            f'- Continuation from the four strongest stage-one outputs: {summaries[1]["trials"]} trials in {summaries[1]["seconds"]:.1f} seconds, with two fresh seeds and three modes.',
            f'- {sum(r["classification"].startswith("published") for r in rows)} counts beat the frozen published table by the prespecified practical gate; zero established new records.',
            f'- {len(audit)} imported witnesses certified; {sum(x["raw_decimal_feasible"] for x in audit)} were feasible at their literal printed radius. Maximum downward repair: {max(D(x["radius_reduction"]) for x in audit):.3E}.',
            '- The N=47 external AI witness passes exactly at 0.073113151 and remains below the published reference.',
            '- N=250 and 400 beat the older pre-2023 baselines, but those advances already exist in the imported current constructions. N=106 historical differences are below our practical gate.','',
            '[Full source-backed radii and certificates](RECORDS.md) · [Gallery](images/GALLERY.md) · [Source/claim audit](AUDIT.md)','',
            '## Did stronger starts leave further headroom?','',
            '| N | Stage one certified r | Continuation certified r | Additional gain | Clears practical gate? |',
            '|---:|---:|---:|---:|---|']
    for r in comparisons:
        report.append(f'|{r["n"]}|{r["stage1"]}|{r["continuation"]}|{D(r["gain"]):+.3E}|{"Yes" if r["meaningful"] else "No"}|')
    report += ['', 'Only N=600 and 700 had meaningful stage-one gains. The other two continuation selections are tie controls chosen by relative gain, not newly discovered superior basins. Continued improvement at a successful count is evidence of numerical room, not priority over the private queue. No statistical success-rate model is fitted to these few dependent trials.','',
               '## Search-arm comparison','',
               '| Stage | Mode | Trials | Beats published gate | Median r / published r | Changed-edge trials | LP failure/time-limit trials | Solver seconds |',
               '|---|---|---:|---:|---:|---:|---:|---:|']
    byn={r['n']:D(r['published_radius']) for r in rows}
    import statistics
    for name,ts in zip(['discovery','continuation'],trials):
        for mode in dict.fromkeys(t['mode'] for t in ts):
            subset=[t for t in ts if t['mode']==mode]
            ratios=[float(D(t['radius'])/byn[t['n']]) for t in subset]
            report.append(f'|{name}|{mode}|{len(subset)}|{sum(t["classification"].startswith("historical") for t in subset)}|{statistics.median(ratios):.8f}|{sum(t["changed_edges"]>0 for t in subset)}|{sum(t["lp_failures"]>0 for t in subset)}|{sum(t["seconds"] for t in subset):.1f}|')
    report+=['','Each trial logs its exact feasible result, even when HiGHS stops at its time limit. Changed-edge counts compare perturbed input with relaxed output and do not prove a new contact topology relative to the published construction. Cold and neighbor starts receive the same short per-trial cap and often have much farther to travel than warm polish. This is not an equal-convergence comparison or proof that those methods are unproductive.','',
             '## Reliability and limits','',
             'The verifier is an independent standard-library implementation that checks all walls and all pairs with arbitrary-precision integers. Ten tests cover positive controls, one-unit overlap, wall failures, wrong counts, duplicate centers, malformed values, local-solver recovery, neighboring counts and seed determinism. The saved N=600 numerical replay agrees within the practical comparison gate; exact witnesses remain the reproducible result.',
             '', 'A continuation setup attempt failed before any search because a relative path was compared with an absolute root. It is preserved as `experiments/continuation-setup-failure`; the path handling was corrected and the complete continuation rerun in a fresh output directory. Stage-one source code is archived under `experiments/stage1/code` and its original hashes remain in its environment record.',
             '', 'Wall-time measurements are descriptive: machine load was not controlled, and a short numerical replay/verification probe overlapped part of discovery. Comparisons of methods or performance per CPU-second would need isolated, interleaved runs. The finite schedule and recorded iteration caps are the reproducible work controls. These runs are far shorter than the hours-per-run prior campaign and do not establish saturation of the mathematical problem.',
             '', '## What would change the recommendation?', '',
             '1. Obtain accessible numerical witnesses and priority dispositions for the pending claims, and refresh the full external table. Do not submit during the published October pause.',
             '2. Have an independent reviewer recheck the verifier and nominate a willing maintainer with explicit review capacity. Keep donor intake paused until then.',
             '3. Run a small, preregistered follow-up from the final certified N=600/700 starts: repeated short sessions versus one continuous session with equal total LP work, report the distribution of certified improvements and the plateau. The current evidence supports trying this locally, not promising records to donors.',
             '4. Enable a narrow launcher only if meaningful gains survive the refreshed frontier and independent review, with enough yield to justify reviewer time. Otherwise keep this as a reproducible negative/partial pilot.',
             '', 'Feasibility verification is inexpensive; review capacity and novelty reconciliation currently limit usable donated work. No remote repository, hub application, publication, or communication was made.']
    report.append('The search-arm column “Beats published gate” counts repeated recovery of local incumbents, not distinct discoveries. Continuation polish supplied essentially all further meaningful N=600 gain; later perturbations added only a numerical-scale increment.')
    (ROOT/'REPORT.md').write_text('\n'.join(report)+'\n')
    print('Built tables, report, frontier and SVG gallery')
if __name__=='__main__':main()
