# Current handoff — 21 October 2026

Use [the pre-release package](research/readiness-20261021/README.md) and
[review brief](research/readiness-20261021/REVIEW.md). New contributors should use the
working-start index and QUICKSTART.md, which inherit the later 500/700/800 proposals.
Independent review, external standing, serial yield and onboarding remain pending.
No message has been sent. The dated original handoff follows for historical context.

---

# Local handoff — no message was sent

Latest local follow-up: [contributor suitability report](research/contributor-20261020/REPORT.md). It found stronger exact experimental witnesses at N=500,700,800; use its `certificates/best/` for any authorized further research after verification. These are proposals pending acceptance, and the original recorded frontier remains unchanged. The short stronger-start tests and longer-call diagnostics are in its experiment tables. No messages were sent.

The 12-count pilot is complete. Read REPORT.md, RECORDS.md and AUDIT.md. Exact geometry
and reproducible artifacts are available; novelty and human review are outstanding.
Novelty reconciliation comes before more search. Never contact record keepers or other
authors on the project's behalf; that is the maintainer's decision.

Numerical follow-up remains useful at N=600, where continuation found a meaningful
additional gain, but later perturbations only polished the same radius. N=700's
continuation increment was below the practical gate. The other tested counts tied the
published table under that gate. A null here does not prove global optimality.

Before further work, run `python3 src/reproduce.py`, inspect `discover/ledger.jsonl`,
and draw a local task with `python3 src/pick.py --seed <32 hex digits>`.
If no seed is supplied, the picker obtains one from the operating system and records it.

```discover
{"v": 0, "kind": "handoff", "task": "reconcile-pending", "scope": "Resolve N=600/700 record novelty before enabling donated sessions", "base": "562aa5aeb8bb558b517008b9404ecb31b0ef9027", "posted_at": "2026-10-20T17:51:53Z", "evidence_level": "local-only", "request": {"question": "Do the certified pilot gains beat earlier pending claims, and is there a willing maintainer?", "first_step": "python3 src/project_inspect.py audit", "success_test": "Hash-pinned comparable witnesses and an explicit review/priority disposition; otherwise retain unresolved status.", "track": "reconcile", "est_minutes": 30}}
```
