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
