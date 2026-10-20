# Featured-pilot suitability: contributor test

**Recommendation: defer inaugural featured status; retain this as a demonstration pilot and a focused research experiment.** This run is more encouraging about initial hill-climbing than the first pilot. It found genuine improvements from already-strong local starts. It did not establish a dependable stream of contributions after those gains are shared, or a consistently superior agent-designed search. The pending external frontier also remains unresolved.

The completed session took **53.7 minutes end-to-end**, starting at 18:31:39 UTC on 20 October 2026. Numerical search ended at 19:15:29 UTC and included **39.76 search-worker wall minutes / 15.34 worker CPU minutes**. Validation and packaging are included in the end-to-end duration. CLOSURE.json records the timestamps.

## What the contributor actually accomplished

The session began from the previous pilot’s strongest exact witnesses at N=400,500,600,700,800. It did not reset to weak layouts to manufacture progress. There were 253 numerical trials across 47 completed blocks: exploration, an interleaved two-seed method comparison, stronger-start continuation, an A/A repeat, and longer-polish diagnostics. Every numerical candidate was converted into an exact rational feasible-coordinate witness.

| N | Final certified radius | Gain over previous pilot | Relative radius gain |
|---:|---:|---:|---:|
|500|0.023455596955367|9.7961867E-8|4.176 ppm|
|700|0.019906357272343|0.000002660338778|133.661 ppm|
|800|0.018638671925985|0.000001079640095|57.928 ppm|

N=400 and N=600 had no additional gain beyond the practical gate. The gate against an exact input is max(10^-10, 10^-8 × radius); comparison with the printed catalogue also adds a 10^-12 rounding guard. The three gains above are real feasible-coordinate improvements, not last-digit recovery. [All radii, source credits and certificates](RESULTS.md).

## Does the next contributor still have a hill to climb?

There is initial headroom, but the succession test is much less encouraging:

- Four fresh stronger-start blocks at N=500 produced no meaningful gain.
- Four at N=800 also produced no gain. Their short inner solves hit time limits, so that alone was not treated as evidence of convergence.
- Four at N=700 all recovered the **same** additional 4.33295063×10^-7 gain, entirely in the initial unperturbed polish. Later perturbations did not improve that new radius. These are four recoveries of one refinement, not four discoveries.
- Final uninterrupted polishing from the newest N=700 and N=800 witnesses reached the solver’s stationarity stopping rule without another gain. The N=800 check completed in about 10 seconds when CPU availability changed, resolving the earlier short-call timeout ambiguity for plain polishing.

This is one contributor session with short per-count compute blocks, not a population of independent 30-minute donors. Four minutes of continuation per count cannot establish mathematical exhaustion. Still, the run does not justify promising early volunteers that they will keep improving the frontier once the first few gains are incorporated. [Full experiment tables and nulls](EXPERIMENTS.md).

## Did agent intelligence make a difference?

There is a useful role for reasoning about the search, but no demonstrated universal advantage. I diagnosed overly disruptive moves, implemented small contact-aware perturbations and differentiable overlap repair, checked the analytic gradient, froze the method, and compared it on fresh seeds.

Across ten paired count/seed comparisons, the new strategy won three, the original won three, and four tied under the practical gate. The same decisions held in the post-hoc comparison at matched completed CPU work. The new strategy won both N=500 pairs, the original won both N=700 pairs, and N=800 split. This supports learning which method suits an instance; it does not support calling the new method generally superior.

The pure-polish controls matter. Unchanged N=500 stayed stationary, while perturbations repeatedly improved it. Longer plain polishing at N=800 improved the old input but stopped below the best perturbed packing. Some initial gains therefore required changing the arrangement, not just finishing the same local solve. Conversely, the additional N=700 continuation gain was ordinary unfinished refinement.

Agent judgment helped with method design, instance selection, diagnosing timeouts and distinguishing feasibility from novelty. Once the method is fixed, most work remains conventional numerical optimization. There was no component ablation or test against a knowledgeable human making the same decisions, and no full comparison against the literature’s strongest solvers. A featured **agent-method-development** challenge would need its own controlled objective and evaluation; that would be a proposed change of emphasis, not a result established here.

## Fit against the launch criteria

| Criterion | Assessment | Reason |
|---|---|---|
| Early tangible progress | Promising initially; uncertain after sharing gains | Three of five deliberately selected counts improved, but stronger-start follow-up mainly recovered one unfinished polish. This is not a 60% general success-rate estimate. |
| Public appeal and explanation | Strong puzzle; modest visual size gain | Equal coins in a square are immediately understandable. Rearrangements and contacts can be shown honestly; the radius increments need a numerical chart. |
| Meaningful research results | Exact lower bounds; novelty unresolved | Feasibility is rigorous. No new world record or global optimum is established. |
| High-end home PC feasibility | Strong | One search worker used 161.6 MiB peak RSS, no GPU, and 15.34 CPU minutes across 39.76 worker wall minutes on an Apple M2. Agent inference cost was not instrumented. |
| Agent intelligence adds value | Mixed, with concrete opportunities | The agent designed and diagnosed methods, but the fixed original search remained competitive. No general strategy advantage was demonstrated. |
| Sustained featured-project supply | Not established | Five selected counts and one session are insufficient to support a broad donor launcher against a partially private external frontier. |

The computer had eight physical cores and 24 GiB RAM, with substantial unrelated load throughout. Resource use is measured; these timings are not an isolated desktop benchmark or a prediction of performance on other hardware. A less busy PC could complete substantially more solver work within a session, but that was not measured here.

## An honest public demonstration

[Before/after packing and close-up](images/demo.svg) · [Certified progress chart](images/progress.svg)

The demo shows N=800 at actual geometric proportions and enlarges the same local region before and after. Changed approximate contacts are visual guides, not the proof. At the 570-pixel square scale, the radius gain is only about 0.000615 pixels, while some centers move visibly. The figure does not exaggerate circle growth. The progress chart uses step changes at completed verified trials, including flat periods.

A suitable explanation is: “We start with a crowded arrangement, try moving small groups of circles, and check whether every circle can become slightly larger. An exact checker tests every wall and every pair. We improved our previous constructions; whether these beat earlier private submissions is still unknown.”

This is a compelling way to explain computational research and certificates. It is a weaker basis for a launch promise that each donor will discover a new record.

## Record standing and what should happen next

The [Packomania table](https://packomania.com/csq/) is dated 10 September 2026. Its [pending queue](https://www.packomania.com/pending-requests.html) includes 557 square candidates spanning 401–1000 and 1,813 spanning 501–9984, among other entries. These are candidate counts and ranges, not evidence of which exact N already have stronger pending witnesses. The latter entry was present in our original snapshot but omitted from the earlier summary; this session corrects that omission.

[Project Aletheia](https://www.projectaletheia.org/findings?view=canonical) specifically claims submitted improvements at N=600,700,800, with catalogue acceptance still pending and no comparable coordinate witness exposed in the material audited here. N=500 also lies inside a pending range. All three new gains therefore remain **published-baseline improvements with unresolved novelty**. [Source recheck and additional AI-search context](SOURCE_UPDATE.md).

Before featuring this as a donated research project, I would require:

1. A refreshed, openly comparable frontier that reconciles the relevant pending witnesses, plus a willing reviewer/maintainer. Administrative review alone would not resolve the productivity question.
2. Several serial full contributor sessions, each inheriting the latest strongest results, with all nulls retained. Predeclare a product-level success threshold before that study; do not reset baselines between donors.
3. A controlled test of a count-adaptive strategy against a strong fixed method portfolio and plain polishing, with fixed CPU budgets and fresh starts/counts. This would test whether agent decisions improve useful yield.

If that study mostly repeats existing packings or yields only the first unfinished refinement, keep the visual teaching/demo role and defer the record-hunting launcher. The present result is a reason to investigate selectively, not evidence that the entire circle-packing problem is exhausted.

## Evidence and scope of checking

The independent geometric checker uses only integer arithmetic for all walls and pairs. The separate accounting checker uses exact fractions to reject invented radii, changed baselines, wrong counts and false tiny improvements. Nineteen tests passed; a numerical replay of the first N=500 improvement reproduced its certified radius exactly. The final verification receipts are in `logs/verification.json`, `logs/fresh-clone-verification.txt`, and `verifications/`.

Run from the project root:

```sh
python3 research/contributor-20261020/code/verify_session.py
python3 research/contributor-20261020/code/test_accounting.py
```

TASK.json, SOURCES.json and VERIFY.json describe scope, provenance, replay commands, dependency pins and remaining questions. The code, explicit starts, all trial certificates, negative results and retained SVGs are included. The conditional interior-point diagnostic was prepared but not executed because the final default solve finished promptly. The initial pilot package was also repaired to include its missing README/source index, and package validation now checks both result packages; its numerical evidence was unchanged.

Everything remains local. These are author checks by the same agent that assembled the experiment, not independent human review or maintainer acceptance. The original project frontier was not promoted; this package contains the newer experimental proposals. No remote repository, publication, record submission or author communication was made.

Verification note: the first full check passed 305 certificates and 57,014,150 pair checks, but its elapsed-time field reused a radius variable. That reporting bug was fixed and the full check rerun; the first receipt is retained as `logs/verification-initial-timing-bug.json` and its time must not be used. The geometry and optimization code were unchanged.

Final validation: a fresh local checkout at `fb443668c28573b90c058440085f7dcfcb2878c5` passed all 305 certificates and integrity checks in 82.18 seconds. A subsequent quote-only syntax fix was checked against Python 3.10 grammar across all 21 source files; the mathematical checks and inputs were unchanged. Runtime verification used local Python 3.14, and numerical optimization used the pinned Python 3.12 environment. The result package occupies about 24 MiB.

```discover
{"v": 0, "kind": "finding", "task": "continue-strongest", "scope": "Local contributor trial at N=400,500,600,700,800: three certified gains over prior pilot; stronger-start follow-up adds one N700 polishing refinement; featured launch deferred; novelty unresolved.", "scope_status": "refined", "base": "e11c81713dd9b19696a95751eac809ce451c83fb", "posted_at": "2026-10-20T19:25:24.348311+00:00", "evidence_level": "author-checked"}
```
