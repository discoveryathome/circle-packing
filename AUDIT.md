# Source and frontier audit — 20 October 2026

The target is **equal radii in a square**, maximizing the common radius. A certificate establishes a feasible lower bound on the unknown optimum, not optimality. Raw source snapshots and their SHA-256 digests are in `sources/manifest.json`. No source repository was executed, no author was contacted, and no submission was sent.

## Claims and evidence

| Claim | Audit disposition | Primary source |
|---|---|---|
| Packomania is a useful starting incumbent catalogue | Confirmed; its `csq` table is dated 10 September 2026. Rounded coordinates require exact rechecking. It is not a completeness guarantee for today's frontier. | [Equal circles in a square](https://packomania.com/csq/) |
| All published decimals are strictly feasible at their printed radius | False for many downloaded witnesses. See `experiments/baseline-audit.json`: exact checks and safe downward radius adjustments, without changing the printed centers. This is expected rounding behavior, not evidence against the underlying constructions. | [Coordinates, example N=600](https://packomania.com/csq/txt/csq600.txt) |
| Beating the printed table establishes a new record | Unverified. The 17 October queue includes 557 `csq` candidates spanning 401–1000, 250 spanning 1015–9996, and 1,813 spanning 501–9984. Values and exact membership are not public there. The homepage requests a pause in October submissions. | [Pending requests](https://www.packomania.com/pending-requests.html), [homepage](https://www.packomania.com/) |
| Recent independent AI work already has equal-circle candidates at 600, 700, 800 | Publicly claimed by Project Aletheia on 31 August 2026; explicitly pending catalogue verification. The findings and registry pages do not expose numerical radii or downloadable coordinate witnesses. ART-085 is a label, not an accessible certificate. Independent feasibility and priority remain unresolved here. Do not confuse this independent lab with DeepMind's similarly named agent. | [Findings](https://www.projectaletheia.org/findings?view=canonical), [registry policy](https://www.projectaletheia.org/datasets) |
| MinMax Arena's AI result for 47 beats the external record | Contradicted. Its exact public witness passes here at r=0.073113151, below Packomania's printed 0.073113151271. The author's method is lattice polishing of existing centers. The page itself disclaims beating the external reference. | [N=47 witness and method](https://minmaxarena.com/en/problems/square-circle-packing/p01-n47-v1) |
| MinMax's background statement that 31–33 remain open is current | Contradicted by Markót's computer-assisted optimality proofs for 31,32,33. This illustrates why an arena's background text is not the authoritative proof frontier. Selected pilot counts are much larger. | [Markót 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8550790/) |
| ZeroThesis is searching the same problem | Confirmed. Its public challenge describes equal circles; its displayed aggregate score is below 1. Packomania separately credits Madala/ZeroThesis with catalogue candidates at 3000 and 9996. Neither establishes a new incumbent for the 12 selected counts. | [Challenge](https://zerothesis.com/challenges/circle-packing-square), [catalogue update history](https://packomania.com/csq/#Updates) |
| AlphaEvolve/ShinkaEvolve-style N=26/32 sum-of-radii results are equal-circle records | Wrong objective. Liang's independently checkable repository explicitly maximizes the sum of **unequal** radii and compares against `csqv`. Useful algorithmic context, excluded from the equal-radius record table. | [Liang source repository](https://github.com/jasonzliang/circle-packing-sota) |

This is a bounded public-source audit, not an exhaustive novelty search. Pending submissions can defeat a priority claim even if they were not publicly downloadable. A date on a fetched page is distinguished from our retrieval time.

## Literature informing the search

- [Addis, Locatelli and Schoen, 2005](https://optimization-online.org/2005/03/1088/): basin hopping and improvement from previous incumbents motivate the perturb-and-relax track.
- [Huang and Ye, 2010](https://doi.org/10.1016/j.orl.2010.07.004): vacancy search motivates deletion, insertion into holes, and contact disruption.
- [Lai, Hao, Xiao and Glover, 2023](https://doi.org/10.1287/ijoc.2023.1290): perturbation-based thresholding combines penalty minimization and container adjustment. The paper reports 156 improved cases up to 400; its experiments used 20 runs with size-dependent budgets of 2–12 hours per run. Our seconds-long trials are a pilot, not a competitive replication of that compute budget. The [author manuscript](https://leria-info.univ-angers.fr/~jinkao.hao/papers/LaietalJOC2023.pdf) is frozen locally. Table 6 was visually inspected. The pilot implements an independent sparse LP local solver, not PBTS.
- [Amore and Morales, 2022 version](https://arxiv.org/abs/2102.01537v2): separate construction and refinement algorithms motivate testing a second search stage from the strongest stage-one outputs.
- [Markót, 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8550790/): interval global optimization distinguishes proving optimality from finding a feasible construction. This pilot does the latter with exact rational coordinates.
- [Khajavirad, 2024](https://arxiv.org/abs/2404.03091): convex relaxations are relevant to upper bounds; they do not turn a local stationary point into a proof of optimality.

## Selected instances and purpose

| N | Selection rationale |
|---:|---|
|100|Lower-cost mature baseline, seven reported rattlers; tests whether local movement creates meaningful room.|
|106|Smallest improved case in the 2023 study; exceptionally close competing packings make a useful precision stress test.|
|134|Vacancy-search history and irregular contact structure; medium-size neighbor transfer test.|
|150|Medium-size case between heavily studied counts; balances cost and geometry.|
|200|Historical boundary of older extensive sweeps; tests transfer at a mature larger instance.|
|250|Documented improvement over the pre-2023 baseline; catches rediscovery mislabeling.|
|300|Upper end of the medium tier; baseline reported repeatedly reachable in PBTS.|
|400|Upper boundary of the 2023 campaign; known historical gain must not be called new.|
|500|Larger search space and near the lower end of a large pending-submission range.|
|600|Independent pending candidate; explicit test of whether catalogue polish recovers an already-claimed gain.|
|700|Same, at higher local-search cost.|
|800|Same, tests scaling and continuation headroom.|

“Promising” means a reason to test, not an asserted likelihood of a record. N=47 is an additional external precision control, not one of the 12 search targets. N±1 witnesses are downloaded as initialization assets. Counts 3000 and 9996 are excluded from the short-session pilot for cost. No global upper bound is proved for the selected cases.

## Historical comparison policy

`data/historical.json` transcribes **pre-improvement** side lengths from Tables 4 and 6 of Lai et al. Convert unit-radius container side L to unit-square circle radius r=1/L. For a printed L with nine decimal places, the comparison guard uses L±10^-9 and inverts its endpoints. This is a conservative publication-precision envelope, not a theorem about the original authors' numerical errors. Historical advantages at 250 and 400 already occur in today's Packomania files. For 106 the published historical difference is extremely small and does not pass our practical novelty gate.

The current-table comparison requires certified r > printed_r + 10^-12 + max(10^-10, 10^-8·printed_r). Smaller gains are recorded as numerical ties even if their exact signs are positive. This conservative policy deliberately can miss mathematically real tiny gains. It prevents rounding recovery or LP tolerance noise from masquerading as useful new records. The guard is a screening rule, not an upper bound on the best packing represented by a source configuration.

Even a gain that passes this screen is only an **improvement over the frozen published baseline** until accessible independent claims and the maintainer's pending queue have been reconciled. The independent Aletheia claims specifically block unqualified novelty language at 600,700,800.

Follow-up source recheck: [contributor-session audit](research/contributor-20261020/SOURCE_UPDATE.md). The 1,813 entry was present in the original snapshot and omitted from the first summary; no change of queue date is inferred.
