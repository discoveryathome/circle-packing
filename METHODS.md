# Model, search and certificate contract

For N≥1, maximize r subject to r≤x_i,y_i≤1−r and (x_i−x_j)^2+(y_i−y_j)^2≥4r² for every pair. The maximum exists by compactness. A construction gives a lower bound; no experiment here determines the exact maximum for arbitrary N. N=1 is r=1/2.

For N≥2 the optimizer places points p_i in [0,1]² and maximizes their minimum separation d. Map to circles by r=d/[2(1+d)] and c_i=r+(1−2r)p_i. The inverse is p_i=(c_i−r)/(1−2r), d=2r/(1−2r). Optimizer score d, radius r, side L=1/r for unit-radius circles, and density Nπr² must never be compared interchangeably.

## Local solver

At each step, compute unit vectors u_ij along current pair displacements. Solve a sparse LP maximizing d subject to u_ij·(p_i+δ_i−p_j−δ_j)≥d, a coordinate-wise trust box, and [0,1] bounds. This supporting-plane condition implies the true norm inequality in exact arithmetic. LP output is only a numerical proposal; all final acceptance uses the separate verifier. A pair can approach by at most 2√2 times the coordinate trust radius. The solver omits only pairs beyond the maximum permitted d plus that amount, rebuilds the set each iteration, and recomputes *all* distances to score the result.

Perturbations include small Gaussian moves, larger subset moves with Metropolis acceptance between relaxed basins, rotation of a small cluster to disrupt contacts, and occasional relocation into a sampled vacancy. Neighbor initialization removes a circle from N+1 or inserts a circle into a sampled large hole in N−1. A staggered lattice arm supplies a cold-start control. Contact counts and symmetric differences are logged as approximate diagnostics: they are label-dependent and are not graph-isomorphism proofs. A changed labeled edge set alone is not proof of a novel packing topology.

The solver always retains the best exact certificate separately from the current basin. Every trial has a fixed seed derived from [seed,N,mode index]. Continuation ranks the stage-one outputs by relative gain over the published baseline and selects four. It then runs two new seeds and three modes from those saved constructions. If fewer than four counts improve meaningfully, the remaining cases are explicitly tie controls. No claim that selection is an unbiased experiment is made.

## Rigorous feasible-coordinate certificate

A JSON certificate contains one positive integer denominator Q, one positive integer radius numerator R, and N pairs of integer coordinate numerators (X_i,Y_i). Integers are strings to avoid lossy JSON readers. Its physical coordinates are exactly X_i/Q,Y_i/Q and all radii are exactly R/Q. The standalone standard-library verifier checks:

1. The expected N, schema, shape and integer types; no NaN, infinities or JSON floats.
2. R≤X_i,Y_i≤Q−R for every circle.
3. (X_i−X_j)²+(Y_i−Y_j)²≥4R² for every unordered pair.

Tangency is allowed. These integer inequalities prove containment and non-overlap without square roots, interval libraries, or floating-point slack. Count checking is part of verification: `--n N` binds a witness to a record-table row.

Certificate creation rounds centers to a 10^15 grid, computes the exact minimum wall distance and minimum pair squared distance, and chooses R as the smaller of the wall cap and floor(isqrt(min_pair)/2). This is the largest integer radius numerator feasible for those rounded centers. It certifies an explicitly shrunken construction; it does not certify the original floating-point optimum or claim an exact optimum. Independent `verify.py` does not import the optimizer, NumPy, SciPy, or the certificate builder. Independence is at implementation level; a different human/team has not yet reviewed it.

Printed Packomania centers are translated from a square centered at zero by adding exactly 1/2. The common published radius is checked for consistency across source lines. Raw printed-radius checks and the adjusted exact radii are both retained. SVGs are generated from accepted certificate values; SVG rendering itself is not a proof.

## Reproduction and resource limits

The cheap result check reads stored witnesses offline. Full stochastic reruns require the pinned numerical dependencies. Each trial has at most 40 LP solves and a wall-clock cap; the stages also have limits and a finite schedule. An LP time limit is passed to HiGHS. Certificate checks/file writes can extend a stage beyond its launch cutoff by the duration of one trial's postprocessing. `environment.json` records code hashes, versions, host and seeds. Solver outputs can differ across hardware/versions or if the wall cap interrupts at a different iteration. Exact certificates and their checks are deterministic regardless of solver reproducibility.

For iteration-controlled replay, use `src/replay.py`: replay the recorded LP step count for each trial with a generous time cap, compare scores within the declared practical threshold, and retain different feasible witnesses. Checkpoints save every trial's certificate and its origin; solver success is not acceptance. The cold-start and neighbor arms are substantially harder than polishing incumbent coordinates and must be reported separately.
