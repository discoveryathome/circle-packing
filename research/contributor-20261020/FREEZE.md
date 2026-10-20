# Strategy freeze before held-out evaluation

Frozen strategy/code commit: af6be839e2c83fa04353dcf4969af7a54858409d.

Exploration has recovered the same meaningful N=500 gain with both methods. Smaller moves repair more readily, but this has not yet established a superior final radius. No strategy changes were made after inspecting the exploratory results. The implementation, parameters and mode order now remain fixed through the matched and continuation stages.

Held-out schedule: 5 counts × 2 methods × 2 fresh seeds, 45 seconds per block, alternating method order and reversing count order for the second seed. Both methods use the original pre-session input set. Common unperturbed polishing is reported separately from perturbation-derived gains. Wall timing is descriptive under shared load; CPU work and solver steps must accompany it.

After the held-out runs, freeze the strongest verified outputs at the two successful exploratory counts, N=500 and N=800. Run 2 methods × 2 fresh seeds × 2 counts for 60 seconds each from that stronger common input set. This is the next-contributor check, and will not be pooled with initial-start success rates. Add one 60-second original-method repeat at N=500 using exploratory seed 0 as an A/A variability check. This repetition uses the old frozen input, not the continuation start.

Total scheduled numerical block budget: 600 seconds exploration + 900 held-out + 480 continuation + 60 A/A = 2,040 seconds (34 minutes). Startup, certificate checking and final writes can cause small overruns. End-to-end session target remains about 45 minutes, inside the user's 30–60-minute range.

## Diagnostic added at 18:46 UTC, before held-out results

The final exploratory N=800 targeted block improved repeatedly while the original arm's initial 18-second polish had hit its budget. This creates a confound: small perturbations may simply permit more polishing time. Add a **polish-only** control from the original frozen N=500 and N=800 starts, up to 90 seconds / 3,000 LP steps each, with the same stationarity stopping rule. It runs after the matched comparison and before continuation. N=500 distinguishes a genuine escape from its previously stationary start; N=800 tests unfinished local convergence. This adaptive diagnostic is reported separately and is not a new frozen-strategy arm. It adds at most three minutes, keeping the full session within the user's 30–60-minute budget.

## Timing analysis added at 18:50 UTC

The shared machine gave paired held-out blocks materially different CPU availability. Add a descriptive, post-hoc sensitivity check: for each matched pair, use the smaller total trial CPU budget, retain only complete trials within that budget, and compare best certified radii including the original start. This does not interpolate unobserved trajectories, remove within-trial wall-cutoff effects, or establish a statistical speedup. It is labeled post-hoc and supplements, rather than replaces, the predeclared equal-wall comparison.

## Additional successful count at 18:53 UTC

Held-out original-method seed 101 improved N=700 after its unperturbed polish had stalled. Add N=700 to the frozen stronger-start set and give it one fresh seed (203), one 60-second block per method, after the predeclared N=500/800 continuation. This is an adaptive addition, not part of the original two-count continuation design, and adds two minutes. All three newly successful counts will therefore receive stronger-start tests.

## Replicate the now-strongest new count, 18:56 UTC

Original-method held-out seed 102 improved N=700 by 2.227e-6, substantially more than seed 101. Give N=700 a second fresh continuation seed (204), reversing method order, so all three successful counts have two seeds × two methods × 60 seconds. This adds a further two minutes; the bounded end-to-end session is expected to be roughly 45–50 minutes. The waiting continuation scheduler was reloaded before it launched any numerical work; no trial was interrupted or discarded.

## Distinguish a timeout from a plateau, 19:09 UTC

Every first- and second-seed N=800 continuation call was hitting the solver time limit; its initial polish completed only two LP steps before a third timed out, consuming roughly 3.5 CPU seconds in 18 wall seconds. A null under this regime cannot support a local-convergence claim. Add a final uninterrupted polish diagnostic at N=700 and N=800, each up to 120 wall seconds / 3,000 LP steps, starting from the strongest witnesses after all short continuations. N=500 already reached the stationarity stopping rule in its unperturbed calls. This adds at most four minutes and keeps the session inside 60 minutes. Report this adaptive diagnostic separately. If it improves, the result supports better scheduling/checkpointing, not a newly invented search neighborhood.

## Conditional final solver diagnostic, 19:11 UTC

If the final N=800 long-call diagnostic hits its limit or takes more than 60 seconds, test an otherwise identical LP method with `method="highs-ipm"` explicitly selected, from the **same** frozen strong-polish input, with a 120-second cap. This is a single engineering diagnostic of the slow inner solve, not a third arm in the matched search study. If the default solve finishes promptly, omit this extra run. No more search stages will be added; finish verification and reporting within the 60-minute session limit.

## Search closed, 19:15:29 UTC

The final strong-start N=700 and N=800 calls both reached the stationarity stopping rule, in about 3.6 and 10.1 seconds respectively, without a gain. The conditional interior-point experiment was therefore **not run**. Its two prepared source files remain as an explicitly unexecuted diagnostic, not as tested evidence. No further numerical searches were added.
