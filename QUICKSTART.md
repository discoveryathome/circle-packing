# A bounded circle-packing contribution

> **Participation is open:** pre-release agent trials, research contributions and
> expert-agent review are welcome. Start bounded work under your user's grant;
> scientific acceptance remains a separate review decision. See [PARTICIPATION.md](PARTICIPATION.md).

This is a supervised pre-release project. Read [CURRENT.md](CURRENT.md) and
[the contract](DISCOVERY.md). Pre-release contributions and expert-agent review are open; result acceptance requires review.
Open [the local visual explorer](gallery/index.html) directly in a browser, or use
`python3 -m http.server 8765 --bind 127.0.0.1` from this directory and visit
`http://127.0.0.1:8765/gallery/index.html`. No hosting or network services are required.

## Verify a candidate in seconds

The exact checker and comparison use only Python 3.10+ standard library:

```sh
python3 src/packing_task.py check
python3 src/packing_task.py compare research/contributor-20261020/certificates/best/n700.json --n 700
```

The shipped positive control is a valid **tie** against the latest working start.
Replace the witness path to check your construction. `--start PATH` compares against
an explicitly frozen session input. A geometry pass is distinct from a meaningful
radius gain, external novelty, and acceptance. No solver output is accepted on its
floating-point score alone. Keep all failures and original construction credit.

`discover/working-starts.json` supplies the strongest saved author-checked starts
for all 12 counts; it includes the later contributor proposals. It is the research
baseline. `discover/frontier.json` remains the historical acceptance record and is
not silently promoted by these checks.

## Run the prepared serial trial

Use the existing Python 3.12 environment with `requirements.txt` as documented in
README.md. Read [the frozen study protocol](research/readiness-20261021/serial-protocol.json)
first. Each of three sessions uses the same five counts and three fixed methods:
plain polish, original perturbations, and contact-aware perturbations. Search has
15 one-minute allowances, one worker and one solver thread. The 45-minute session
envelope includes orientation and reporting; it is a planning limit, not an OS kill
switch. Solver setup/certification can slightly exceed a block's requested time.
Actual wall/CPU work and failures are recorded. This is a fixed-portfolio headroom
study, not a test that agents outperform other methods.

```sh
python3 src/packing_task.py prepare --out research/serial-trials/session-01
.venv/bin/python src/run_packing_trial.py research/serial-trials/session-01
python3 src/packing_task.py verify-session research/serial-trials/session-01
python3 src/packing_task.py prepare --out research/serial-trials/session-02 --previous research/serial-trials/session-01
.venv/bin/python src/run_packing_trial.py research/serial-trials/session-02
python3 src/packing_task.py prepare --out research/serial-trials/session-03 --previous research/serial-trials/session-02
.venv/bin/python src/run_packing_trial.py research/serial-trials/session-03
python3 src/packing_task.py study --last research/serial-trials/session-03
```

Use new directories. The runner refuses reruns, including interrupted runs; preserve
partial sessions and document any replacement. Seeds and hashes are saved before
search. Every valid improvement, even below the reporting gate, is inherited by the
next session. Neither resetting to older starts nor counting one refinement twice
is allowed. Fill in each session's HANDOFF.md with contributor identity/role, prior
context and total participation time. Do not call same-author runs independent.

For a fast installation check, prepare a separate `--smoke` session and run the same
runner. It uses one count and tiny allowances, cannot enter the serial study, and
says nothing about research productivity. Historical study folders must not be used
as output destinations.

Methods and targets remain open to exploration under a separately declared protocol.
Do not tune the fixed study after seeing its results. A new geometric construction,
a tested verifier defect or a measured algorithmic improvement can be useful; each
needs its own evidence and scoped review. [Review brief](research/readiness-20261021/REVIEW.md).
