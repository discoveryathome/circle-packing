# Experiment evidence

These are descriptive results from one heavily loaded Apple M2 machine. No population success probability or statistical speedup is inferred. All counts use common original starts in the held-out comparison; continuation uses a separate stronger frozen input set.

## Held-out paired comparison

Both arms received 45-second block budgets. “Winner” requires a radius difference beyond the practical gate. The CPU-matched sensitivity analysis retains only complete trial endpoints within the smaller observed CPU budget; it was added after timing imbalance was observed.

| Seed | N | Original best r | Targeted best r | Wall-budget winner | Common CPU s | CPU-matched winner |
|---:|---:|---:|---:|---|---:|---|
|101|400|0.026202507076218|0.026202507076591|tie|13.54|tie|
|101|500|0.023455589971477|0.023455596955163|targeted|22.04|targeted|
|101|600|0.021479896578172|0.021479896578178|tie|10.83|tie|
|101|700|0.019903807317692|0.019903696933814|original|29.13|original|
|101|800|0.018638080112653|0.018638671925985|targeted|18.84|targeted|
|102|400|0.026202507076218|0.026202507076591|tie|9.79|tie|
|102|500|0.02345559340335|0.023455596954435|targeted|6.41|targeted|
|102|600|0.021479896578172|0.021479896578172|tie|15.64|tie|
|102|700|0.01990592397728|0.019903696933565|original|17.52|original|
|102|800|0.018638173610066|0.018638082179971|original|32.49|original|

Wall-budget outcomes: {'tie': 4, 'targeted': 3, 'original': 3}. CPU-matched outcomes: {'tie': 4, 'targeted': 3, 'original': 3}.

## Stronger-start continuation

Two methods × two seeds at N=500/800; two additional seeds per method at N=700, added after its held-out discovery. Each block starts from the same frozen best witness for that N. This is a deliberately selected promising subset, not a random sample of all N.

| Seed | N | Method | Stronger starting r | Best final r | Additional gain | Clears gate? | CPU s | Wall s |
|---:|---:|---|---:|---:|---:|---|---:|---:|
|201|500|original|0.023455596955163|0.023455596955163|+0.000E-12|no|14.97|60.22|
|201|500|targeted|0.023455596955163|0.02345559695532|+1.570E-13|no|13.75|60.72|
|201|800|original|0.018638671925985|0.018638671925985|+0.000E-12|no|10.59|62.43|
|201|800|targeted|0.018638671925985|0.018638671925985|+0.000E-12|no|11.35|62.69|
|202|500|original|0.023455596955163|0.023455596955163|+0.000E-12|no|16.53|60.11|
|202|500|targeted|0.023455596955163|0.023455596955367|+2.040E-13|no|25.99|59.92|
|202|800|original|0.018638671925985|0.018638671925985|+0.000E-12|no|12.05|64.08|
|202|800|targeted|0.018638671925985|0.018638671925985|+0.000E-12|no|10.13|63.02|
|203|700|original|0.01990592397728|0.019906357272343|+4.333E-7|yes|25.99|60.21|
|203|700|targeted|0.01990592397728|0.019906357272343|+4.333E-7|yes|23.27|60.38|
|204|700|original|0.01990592397728|0.019906357272343|+4.333E-7|yes|34.61|60.10|
|204|700|targeted|0.01990592397728|0.019906357272343|+4.333E-7|yes|33.53|60.20|

## Plain longer polishing and A/A repeat

The first polish-only control uses the unchanged pre-session input, no perturbation and up to 90 seconds / 3,000 LP steps. The final strong-polish diagnostic uses the newest post-continuation witness and up to 120 seconds. Stationarity may stop either early. A/A repeats original N=500 seed 0 at a later wall-clock time. These diagnostic controls were added during the session and are not randomized treatment estimates.

| Phase | N | Best r | Gain from its input | CPU s | Wall s |
|---|---:|---:|---:|---:|---:|
|aa-original-repeat|500|0.023455596952977|+9.796E-8|37.20|59.78|
|exploration-original|500|0.023455596952977|+9.796E-8|15.49|59.95|
|long-polish|500|0.0234554989935|+0.000E-10|1.40|6.24|
|long-polish|800|0.018638081785221|+4.895E-7|13.91|62.87|
|strong-polish|700|0.019906357272343|+0.000E-12|2.41|3.56|
|strong-polish|800|0.018638671925985|+0.000E-12|4.87|10.12|

## Trial accounting

“Above start” includes repeated recovery, not independent discoveries. “Recovered” includes ties within the gate, excludes initial unperturbed polish, and compares moves of different disruption sizes. It is a repair diagnostic, not a fair hardness ranking of neighborhoods.

| Stage | Method | Trials | Above input gate | Recovered / perturbed | LP steps | LP failure/limit trials | CPU s | Wall s |
|---|---|---:|---:|---:|---:|---:|---:|---:|
|exploration|original|33|3|2/28|203|25|95.97|300.16|
|exploration|targeted|36|7|16/31|169|16|112.58|299.89|
|heldout|original|54|9|10/44|415|34|215.01|450.83|
|heldout|targeted|50|11|28/40|227|20|201.15|449.66|
|continuation|original|36|4|2/30|191|31|113.98|363.81|
|continuation|targeted|31|8|13/25|128|18|117.24|363.61|

Total: 253 saved trial witnesses; 47 completed blocks; 2385.57 worker wall seconds; 920.41 worker CPU seconds; 161.6 MiB peak worker RSS.

## Interpretation limits

- Repeated seeds are a small formative check; no statistical confidence interval is warranted.
- A local stationary solution is not a global optimum. A null in this budget does not establish that the mathematical instance is saturated.
- Wall time includes certificate construction and checking. CPU timing counts this worker, not unrelated system processes or agent inference.
- Algorithms were not compared against a full PBTS or other state-of-the-art implementation. These are the existing pilot solver and a session-designed variant.
- The trial log key `gain_vs_session_start` means gain from that block’s chosen input; continuation blocks use the stronger input. Global session gains in RESULTS.md and summary.json are independently recomputed from the original frozen witness.
- Source code hashes were captured per block. The paired-arm search code froze at af6be839e2c83fa04353dcf4969af7a54858409d. Later additions were separately logged polishing controls, analysis, exact accounting, visualization and scheduling; the two compared strategies stayed unchanged.
