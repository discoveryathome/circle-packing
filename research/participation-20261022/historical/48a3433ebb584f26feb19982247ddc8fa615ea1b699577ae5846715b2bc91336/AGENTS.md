# Agent entry

Read `CURRENT.md`, `QUICKSTART.md` and `DISCOVERY.md`, then `AUDIT.md`, `REPORT.md`, and the current `discover/frontier.json`.
This is a published research proposal at https://github.com/discoveryathome/circle-packing.
There is no agreed maintainer or hub consent. Donor intake is disabled. Work only within
the user's explicit scope. Repository publication was authorized on 2026-10-20; that
authorization does not extend to hub PRs, author contact, or record submissions.

Start with `python3 src/reproduce.py`; this needs only Python's standard library.
For numerical work use the pinned local environment described in `README.md`.
Choose local follow-up work with `python3 src/pick.py --seed <32 hex digits>` and inspect
`discover/ledger.jsonl` plus `HANDOFF.md` for overlap. Record an OS-generated seed if none
is supplied. Do not claim a new record from a positive floating-point delta.

All accepted constructions must pass `python3 src/verify.py WITNESS --n N` with exact
integer arithmetic, have an SVG, and pass the comparison policy in `AUDIT.md`.
Record every negative experiment and its scope. Changes to the verifier require
adversarial tests; changes to the frontier require an explicit review record. Evidence
here is author-checked; a separate implementation is not a separate reviewer.

For new research use `discover/working-starts.json` and `src/packing_task.py`.
The working starts include newer author-checked proposals; they do not promote the
formal frontier. Keep all historical packages immutable. Serial sessions must inherit
the preceding session's exact best witnesses. The full study remains unperformed.
