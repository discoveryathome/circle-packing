# A 45-minute contributor test

This local follow-up asks whether early volunteers can repeatedly improve strong equal-circle packings, whether intelligent algorithm changes help, and whether the result makes a compelling and honest public demonstration.

- `DESIGN.md`: prospective design and success criteria.
- `session.json`: start time, hardware, OS-generated seed, initial input hashes and base commit.
- `inputs/nN.json`: previous pilot's strongest exact witnesses; never overwritten.
- `code/run.py`: bounded search, exact certification and all-attempt logging.
- `code/targeted.py`: session-designed contact moves and elastic repair.
- `code/frozen/`: the original optimizer, certificate maker and independent verifier.
- `logs/`: negative and positive trials, per-block resources, source hashes and timing.
- `certificates/`, `images/`: exact feasible results and SVGs of each retained block result.
- `SOURCE_UPDATE.md`: current claims and correction to the initial queue summary.

Offline verification from the project root, with only Python's standard library:

```sh
python3 research/contributor-20261020/code/verify_session.py
```

Numerical rerun in the project's pinned environment (choose a fresh phase name):

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python research/contributor-20261020/code/run.py --phase my-local-original --arm original --counts 500 --seconds 60 --replicate 301
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python research/contributor-20261020/code/run.py --phase my-local-targeted --arm targeted --counts 500 --seconds 60 --replicate 301
```

`--inputs certificates/PHASE` starts another contributor from a stronger saved phase. The default `inputs` always means the frozen pre-session frontier. Never overwrite phase folders.

A numerical replay of one original attempt, using its recorded LP iteration budget:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python research/contributor-20261020/code/replay_trial.py exploration-original 500 1 --output research/contributor-20261020/replay-n500.json
```

The replay can differ if the original last LP hit a wall-time limit; the recorded exact witness remains the portable, independently checkable result. Elastic-repair attempts replay the saved target and recorded iteration budget. Identical floating point trajectories across hardware are not promised.

No remote repository, record submission, or author communication is part of this session. External standing remains unresolved; these are certified feasible constructions and measured search results, not accepted world records.

## Results and verification contract

The final [assessment](REPORT.md), [exact radius table](RESULTS.md), [experiment comparison](EXPERIMENTS.md), [progress chart](images/progress.svg), and [packing close-up](images/demo.svg) summarize this session. TASK.json records scope and open questions; SOURCES.json pins the base commit, input Git blobs and live hashes; VERIFY.json gives replay commands, dependencies and timeouts.

Every retained experimental construction has an SVG and an exact feasible-coordinate certificate. These are author-checked experimental proposals. The project's original recorded frontier is preserved pending its stated review process; this package does not claim maintainer acceptance or open donor intake.

The numerical strategy is frozen. Per-block configuration hashes cover the executed optimizer, certificate builder, independent geometry checker and relevant search driver. Later edits to analysis, plot and scheduling helpers are documented in FREEZE.md. Every numerical attempt has its actual starting coordinates, result certificate, solver work, timing and hash. A solver time-limit/failure is not hidden: its best available points are converted into a safely feasible lower-radius witness, which can still be worse than the incumbent.

`code/check_accounting.py` independently recomputes progress classifications with exact fractions. Its adversarial checks reject invented radii, changed baselines, wrong counts and false tiny improvements:

```sh
python3 research/contributor-20261020/code/test_accounting.py
```

## Open next questions

1. **Question:** Does a sequence of full contributor sessions keep improving the latest witnesses? **Why it matters:** Recovering an earlier improvement is not another contribution. **First step:** Verify this package, then preregister a new session from `certificates/best/`. **Blocked by:** Nothing for authorized local work; long-run contributor yield has not been measured.
2. **Question:** Which gains beat earlier pending constructions? **Why it matters:** Feasibility and priority are different claims. **First step:** Read SOURCE_UPDATE.md and RESULTS.md. **Blocked by:** Comparable pending witnesses and independent review; this session did not contact anyone.
3. **Question:** Can a count-adaptive search policy beat a fixed solver portfolio on held-out starts and CPU budgets? **Why it matters:** It would make the role of agent decisions measurable. **First step:** Read EXPERIMENTS.md and preregister a new method with fresh seeds and counts. **Blocked by:** A new experiment is needed; the current method comparison is small and does not isolate individual components.

## Credit

Original construction authors remain attached in RESULTS.md and the project's `data/records.json`. An OpenAI coding agent designed and executed this follow-up, implemented the experimental moves, constructed certificates, audited sources and wrote the assessment. Conventional NumPy/SciPy solvers performed numerical optimization. There was no separate agent, human reviewer, author contact or record submission. Imported webpages and the Aletheia illustration retain their original rights and are audit evidence; the pilot's demonstration figures were generated from its own certificate files.
