# Serial attempt evidence bindings — 23 October 2026

The session checker accepted contradictory successful-attempt provenance and failed-attempt certificates that the runner would never emit. A temporary copy of the retained smoke package passed closed verification even after its successful certificate named the wrong arm, session seed, attempt-input hash or inherited-start hash, with row hashes and summaries refreshed. It also accepted a logged failure with a valid different-radius certificate. These controls expose internal evidence inconsistency, not invalid circle geometry or a defect in the historical run itself.

The current checker now enforces two relationships already emitted by `src/run_packing_trial.py`:

- Successful certificates bind `session_seed`, `arm`, `input_sha256` and `base_input_sha256` to the declaration, attempt log and actual inherited input. Additional provenance keys remain permitted.
- A failure has a nonempty text error and retains the prior best decoded certificate for its own count/arm, initialized from that arm's inherited start. Only a strictly larger radius replaces this best; successful ties preserve the earlier fallback certificate. Equality compares decoded Python values, allowing serialization whitespace/key-order differences.

The runner, optimizer, protocol, geometric verifier, certifier, historical packages and working starts are unchanged. This is not a review of the unavailable 317-attempt continuation-study archive. It does not prove that a solver actually ran or that metadata is authentic.

Base: `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a`; seed: `c68557875f8ed1f9b2d61ce46a7dc42e`, originally drawing verification / verify-adversarial. [Claim](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19142284). This extends the drawn verification task while the separate public-source reconciliation runs.

## Evidence

[results.json](results.json) binds the base/current checker, unchanged verifier, audit and every retained historical-smoke file by SHA-256. It records all negative controls and the finite sequence domain. The saved run used Python 3.12.11 in the pinned local environment.

| Check | Result |
| --- | --- |
| Historical three-attempt N500 smoke summary | Exactly reproduced by both implementations; source files unchanged |
| Successful-provenance contradictions in copies of all three real smoke attempts | 39 controls accepted by the base checker, rejected by the candidate |
| Synthetic invalid fallbacks/error shapes | 42 controls accepted by the base checker, rejected by the candidate |
| Consistent synthetic summary sequences | 93,750 per implementation; zero summary/oracle disagreements |
| New regression suite against base | 12 test methods, 21 failed controls, zero errors; five positive methods pass |
| Candidate full suite | All 32 tests pass, including the original 20 |
| Offline reproduction | 50 certificates and 12 frontier rows pass |
| Fresh installation-only smoke | Three attempts/three blocks, zero errors, closed verification passes; excluded from study |

The finite sequence domain uses four circles on a 2×2 grid, denominator 100, inherited radius 20/100. Each attempt either succeeds at 19/100, 20/100, 21/100 or 22/100, or fails and retains the appropriate earlier best. It enumerates all six arm orders and all `5^6` event choices with two attempts per arm: `6*5^6 = 93,750`. This is a synthetic summarizer domain, not 93,750 full protocol sessions; in particular the current runner emits only one polish attempt per block.

The domain contains 450,000 successful attempts and 112,500 fallback attempts per implementation. Each attempt's geometry has six pairs, giving 3,375,000 attempt-certificate pair checks per implementation, plus the final comparison checks. An integer-radius oracle checks the maximum, polish maximum, meaningful/beyond-polish flags and error count. Exactly `6*(5^6-3^6) = 89,376` sequences have a positive gain above the gate. The report pins a deterministic digest of the complete case stream.

The negative controls include missing/mismatched fields, absent or wrong-shaped provenance, changed fallback geometry, changed fallback metadata, the last successful tie substituted for the retained earlier best, and malformed error values. The unit tests additionally cover inherited-start ties and cross-arm fallback borrowing. All negative geometries in the synthetic domain remain feasible; rejection comes from evidence consistency.

The older synthetic unit fixtures were updated to carry the successful-attempt fields actually written by the runner. Their existing maximum, gate, inheritance and partial-session assertions remain in place. [baseline-unit-results.json](baseline-unit-results.json) and [unit-results.json](unit-results.json) record the red/green counts.

## Fresh smoke and frozen history

The new [smoke package](smoke/session.json) was prepared before execution with OS-generated seed `2774897528bf1504e62fb37973463530`. It uses the unchanged smoke allowance and N500 working start. Inputs, attempt snapshots, output certificates, execution declaration, summary and best witness are retained. It tests installation/integration only; it is not donor-productivity evidence, a new continuation study, independent onboarding or a record proposal. The native study checker rejects its smoke status.

Historical source declarations remain immutable. Because the checker itself is a bound scientific source, full closed verification of an older package must use its pinned implementation checkout. This PR does not rebind old declarations or weaken the source gate. The supplementary historical-summary replay above applies both summary algorithms to the untouched saved files; it does not claim that a changed checker has the old source hash. The fresh smoke binds the new checker normally.

## Replay

At this PR's own checkout, with the unchanged base verifier and assertions enabled:

```sh
python3 -m unittest discover -s tests
python3 research/session-bindings-20261023/audit.py --output /tmp/session-bindings.json
python3 src/packing_task.py verify-session research/session-bindings-20261023/smoke
python3 src/reproduce.py
```

The full unit suite needs the repository's pinned numerical dependencies; the audit and closed verifier use the standard library. The audit takes about 18 minutes in this donation environment, performs no optimization, modifies temporary copies only and makes no network request. It rejects optimized Python invocation. Exact values/hashes/case counts should reproduce; Python description and elapsed time may differ. The fresh smoke is already closed: do not rerun optimization in its folder.

## Limits and credit

This checks the emitted relationships, not solver execution/authenticity, numerical optimization correctness, timing, causal benefit, arbitrary JSON representations, every metadata type, unbounded event histories or all protocol fields. It does not complete independent review of the missing serial-study package, establish novelty/optimality or change a product/acceptance gate.

Author-checked AI assistance under the donor's grant, following the existing checker/runner, retained readiness smoke and earlier verification work. The historical smoke was copied only into temporary control directories. Construction credit for its N500 geometry remains with the Packntile team and the earlier pilot/contributor refinements. All other original construction credits remain in their packages. No historical scientific package, accepted result, frontier or working-start index was changed.
