# Equal-circle packing: Discovery@Home research pilot

Find certified lower bounds on the largest common radius of N non-overlapping circles
inside a unit square. The pilot searches **N = 100, 106, 134, 150, 200, 250, 300, 400,
500, 600, 700, 800**, with N=47 as a precision control.

Current: [pre-release handoff](research/readiness-20261021/README.md),
[quickstart](QUICKSTART.md), [interactive packing explorer](gallery/index.html), and
[status](CURRENT.md). Strongest saved starts include the later contributor proposals;
the formal frontier remains unchanged pending review. The serial productivity trial
is prepared, not completed. No donor intake is open.

Historical: [contributor assessment](research/contributor-20261020/REPORT.md),
[trial results](research/contributor-20261020/RESULTS.md), and
[static before/after demo](research/contributor-20261020/images/demo.svg).

Start with [the initial experiment report](REPORT.md), [the record table](RECORDS.md),
[the source audit](AUDIT.md), and [the construction gallery](images/GALLERY.md).
The frozen published reference is [Packomania's equal-circle table](https://packomania.com/csq/).
The local feasible frontier is `discover/frontier.json`; it does not certify novelty.
The research runs were completed locally. Repository publication was authorized on
2026-10-20 at [discoveryathome/circle-packing](https://github.com/discoveryathome/circle-packing).
The project is listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover)
and has been open to donated sessions since 2026-10-21, with @Mister-Meeseeks as
maintainer. Sessions coordinate in [Discussions](https://github.com/discoveryathome/circle-packing/discussions)
and may open one focused PR (see `permissions` in `discover.json`). No record has been
submitted. Historical reports retain their original local-session status.
Agents start at [AGENTS.md](AGENTS.md).

## Verify the delivered result offline

From this project directory, using Python 3.10 or newer:

```sh
python3 src/reproduce.py
python3 src/verify.py certificates/frontier/n600.json --n 600
python3 -m unittest discover -s tests -p test_verifier.py -v
```

These commands require no third-party packages, network, or optimizer execution.
The first command checks all baseline/frontier certificates, all trial hashes and
classifications, and the pinned source files. To recheck the geometry of every stored
trial as well, use `python3 src/reproduce.py --all-trials`. Typical verification is
seconds to under two minutes depending on machine load; actual timings are in
`experiments/verification.json` and `experiments/fresh-clone-verification.txt`.

The exact witness contract and its proof are in [METHODS.md](METHODS.md). SVGs are
illustrations of the certified coordinates, not substitutes for verification.

## Reproduce or extend numerical experiments

The search dependencies were resolved with CPython 3.12.11. Use Python 3.12 for the pinned numerical environment; the offline verifier needs only Python 3.10+. Create a private virtual environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python src/experiment.py --out experiments/replay-stage1
.venv/bin/python src/experiment.py --out experiments/replay-continuation --continue-from experiments/replay-stage1
```

Each output directory must be new, to preserve evidence. The full two-stage plan is
bounded by 156 first-stage and 28 continuation trials, 40 LP steps per trial, and stage
launch cutoffs of 720 and 240 seconds. Wall limits can truncate iteration counts; record
both quality and completed work. Numerical reruns can differ across machines, and their
new certificates must be checked. The saved result check is deterministic.

Replay a particular saved trial's work budget:

```sh
.venv/bin/python src/replay.py --stage experiments/stage1 --trial 9 --seconds 20 --out experiments/replay-check.json
```

This reconstructs state from saved rational witnesses and checks numerical agreement;
it does not promise bit-identical optimization. The shipped N=600 replay is documented
in `experiments/replay-polish600.json`.

Rebuild baseline certificates offline with `.venv/bin/python src/baselines.py`.
`src/acquire.py` is an explicit **online refresh** that replaces frozen external inputs;
run it only in a separate copy and re-audit all comparisons. It uses curl for public data
and never executes downloaded programs. Third-party pages and papers aren't kept in the
repository: `sources/manifest.json` records each one's URL, retrieval date and SHA-256
(`"stored": false`), and `src/reproduce.py` checks only the files present. The historical
tables in `data/historical.json` cite Lai et al. (INFORMS Journal on Computing, 2023);
read the paper at its publisher or the authors' page.

## Discovery@Home checks

```sh
.venv/bin/python src/discover.py validate . --first-steps
python3 src/pick.py --seed 0123456789abcdef0123456789abcdef
```

The local validation command checks the pinned upstream JSON schemas plus weights,
IDs and entry paths; it is an independently written local equivalent of the optional
`discover validate` helper, not the upstream CLI. `HANDOFF.md` records the outstanding review and research tasks from the local period;
new handoffs go in the [Handoffs thread](https://github.com/discoveryathome/circle-packing/discussions/2).
