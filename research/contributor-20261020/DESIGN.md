# Contributor trial design (written before the first trial)

45-minute wall-clock contributor session, starting 2026-10-20 18:31:39 UTC. Search uses one numerical worker; elapsed time includes orientation, code, source audit, experiments and reporting. This is a formative test, not a statistical estimate of all donors' success probability.

Frozen starting witnesses are the strongest previous local results at N=400,500,600,700,800. The question is whether a second contributor can advance those, not reproduce easy gains against stale baselines. N400 and N500 provide controls alongside earlier successful N600/N700 and externally claimed N800.

1. Five 60-second blocks using the existing perturbation/LP solver, with longer per-call iteration limits.
2. Implement contact-aware smaller perturbations and elastic repair; exploratory blocks guide adaptation.
3. Freeze the strategy, then compare original and new strategies with fresh seeds and interleaved count order, equal wall-time blocks. Report CPU usage because this shared Mac is heavily loaded. This is a controlled software comparison, not proof that an AI agent is necessary.
4. Spend a final budget starting from the strongest newly obtained constructions to test sustained hill climbing.

Meaningful improvement means an exact certified radius gain exceeding max(1e-10,1e-8*r) relative to the frozen exact starting radius. Gains against printed Packomania add its 1e-12 rounding guard. All attempts, including regressions and failed solver calls, are logged. Every reported feasible candidate must pass the independent integer verifier. Certificates prove feasibility, not novelty or optimality.

Featured-project evidence should include repeatable gains beyond the previous frontier, improvement from stronger starts, and a credible way to show progress honestly. A single lucky gain or already-pending external result will not establish sustained contributor headroom. Algorithmic insight can be valuable even when no new geometric record is obtained, but must be labeled separately.

Wall-time budgets imply machine-dependent stopping. Save each numerical starting state, code hashes, exact output and LP iteration count so witnesses can be checked exactly and individual numerical paths can be rerun. Do not promise bit-identical solver results across hardware.
