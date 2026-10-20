# Initial pilot result and recommendation

A subsequent [contributor-session assessment](research/contributor-20261020/REPORT.md) tests stronger starts and agent-method changes. The measurements below describe the initial pilot only.

**Defer broad donated-session launch.** The pilot demonstrates cheap, rigorous verification and some numerical headroom over a frozen catalogue. It does not establish unclaimed record headroom: the successful counts overlap independent pending claims, and no maintainer has agreed to review contributions. A focused local follow-up is justified; a public record-hunting launcher is premature.

## Observed results

- 12 target counts, two discovery seeds, six search modes, plus unperturbed polish: 156 trials in 364.9 seconds.
- Continuation from the four strongest stage-one outputs: 28 trials in 118.8 seconds, with two fresh seeds and three modes.
- 2 counts beat the frozen published table by the prespecified practical gate; zero established new records.
- 37 imported witnesses certified; 3 were feasible at their literal printed radius. Maximum downward repair: 1.137E-12.
- The N=47 external AI witness passes exactly at 0.073113151 and remains below the published reference.
- N=250 and 400 beat the older pre-2023 baselines, but those advances already exist in the imported current constructions. N=106 historical differences are below our practical gate.

[Full source-backed radii and certificates](RECORDS.md) · [Gallery](images/GALLERY.md) · [Source/claim audit](AUDIT.md)

## Did stronger starts leave further headroom?

| N | Stage one certified r | Continuation certified r | Additional gain | Clears practical gate? |
|---:|---:|---:|---:|---|
|600|0.021479792246411|0.021479896578172|+1.043E-7|Yes|
|700|0.019903696913008|0.019903696933565|+2.056E-11|No|
|300|0.030219555704412|0.030219555704457|+4.500E-14|No|
|100|0.051401071774379|0.051401071774379|+0.000E-12|No|

Only N=600 and 700 had meaningful stage-one gains. The other two continuation selections are tie controls chosen by relative gain, not newly discovered superior basins. Continued improvement at a successful count is evidence of numerical room, not priority over the private queue. No statistical success-rate model is fitted to these few dependent trials.

## Search-arm comparison

| Stage | Mode | Trials | Beats published gate | Median r / published r | Changed-edge trials | LP failure/time-limit trials | Solver seconds |
|---|---|---:|---:|---:|---:|---:|---:|
|discovery|polish|12|2|1.00000000|8|3|29.3|
|discovery|local|24|1|0.99999686|24|8|48.7|
|discovery|contact|24|0|0.99979474|24|9|52.3|
|discovery|neighbor-remove|24|0|0.99884490|22|7|41.8|
|discovery|neighbor-insert|24|0|0.99703463|24|10|52.4|
|discovery|lattice|24|0|0.98685652|24|8|47.3|
|discovery|basin|24|0|0.98803546|24|11|57.0|
|continuation|polish|4|2|1.00000136|3|0|7.5|
|continuation|local|8|2|0.99998581|8|3|33.3|
|continuation|contact|8|1|0.99986451|8|4|32.1|
|continuation|basin|8|0|0.98690558|8|4|38.0|

The column “Beats published gate” includes repeated recovery of an already-known local incumbent; it is not a count of independent discoveries. At N=600, the continuation polish supplied essentially all of the additional meaningful gain; subsequent perturbations added only a numerical-scale increment.

Each trial logs its exact feasible result, even when HiGHS stops at its time limit. Changed-edge counts compare perturbed input with relaxed output and do not prove a new contact topology relative to the published construction. Cold and neighbor starts receive the same short per-trial cap and often have much farther to travel than warm polish. This is not an equal-convergence comparison or proof that those methods are unproductive.

## Reliability and limits

The verifier is an independent standard-library implementation that checks all walls and all pairs with arbitrary-precision integers. Ten tests cover positive controls, one-unit overlap, wall failures, wrong counts, duplicate centers, malformed values, local-solver recovery, neighboring counts and seed determinism. The saved N=600 numerical replay agrees within the practical comparison gate; exact witnesses remain the reproducible result.

A continuation setup attempt failed before any search because a relative path was compared with an absolute root. It is preserved as `experiments/continuation-setup-failure`; the path handling was corrected and the complete continuation rerun in a fresh output directory. Stage-one source code is archived under `experiments/stage1/code` and its original hashes remain in its environment record.

Wall-time measurements are descriptive: machine load was not controlled, and a short numerical replay/verification probe overlapped part of discovery. Comparisons of methods or performance per CPU-second would need isolated, interleaved runs. The finite schedule and recorded iteration caps are the reproducible work controls. These runs are far shorter than the hours-per-run prior campaign and do not establish saturation of the mathematical problem.

## What would change the recommendation?

1. Obtain accessible numerical witnesses and priority dispositions for the pending claims, and refresh the full external table. Do not submit during the published October pause.
2. Have an independent reviewer recheck the verifier and nominate a willing maintainer with explicit review capacity. Keep donor intake paused until then.
3. Run a small, preregistered follow-up from the final certified N=600/700 starts: repeated short sessions versus one continuous session with equal total LP work, report the distribution of certified improvements and the plateau. The current evidence supports trying this locally, not promising records to donors.
4. Enable a narrow launcher only if meaningful gains survive the refreshed frontier and independent review, with enough yield to justify reviewer time. Otherwise keep this as a reproducible negative/partial pilot.

Feasibility verification is inexpensive; review capacity and novelty reconciliation currently limit usable donated work. No remote repository, hub application, publication, or communication was made.
