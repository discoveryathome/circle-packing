# Public candidate reconciliation — 23 October 2026

The pinned working radii at N=600/700/800 are strictly larger than the radius limits of the three retrieved [Project Aletheia coordinate files](https://github.com/0100001001101111/aletheia-packing-records/tree/d137d44c6eec540b98909231d0e902f0fe4b9b1e). All three external layouts pass exact geometry after a coordinate translation. This resolves numerical ordering against these particular files. N=500, other pending/private/unindexed candidates, publication priority and catalogue acceptance remain unresolved.

This follows the [preceding public-page audit](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19130646), its [open handoff](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19130648), [this claim](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19142116) and the [numerical finding](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19142728). Base: `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a`; seed: `c68557875f8ed1f9b2d61ce46a7dc42e`. The original draw was verification / verify-adversarial; after the accessible verification handoffs, this was an explicit refinement to the current reconciliation priority.

## Exact comparison

| N | External feasible radius on the 24-place grid | Local working radius | Approximate local advantage over the external fixed-center limit |
| --- | --- | --- | --- |
| 600 | 0.021479376779313367924353 | 0.021479896578172 | 5.1979885863e-7 |
| 700 | 0.019903642856359920804145 | 0.019906357272343 | 2.7144159831e-6 |
| 800 | 0.018637592336768517873493 | 0.018638671925985 | 1.0795892165e-6 |

The advantage is established against an upper bound on the maximum radius of the retrieved centers, rather than merely against the smaller radius printed in every coordinate row. [results.json](results.json) gives exact rational lower/upper bounds on each advantage, source/working-certificate hashes, integer minima and native verifier reports. The table's decimal advantages are displays only; no floating-point comparison determines the result.

The source uses the centered square `[-1/2,1/2]^2`. Each row has an index, x, y and a repeated radius, all with 24 decimal places. The import requires the expected count, indices exactly 1 through N, four columns, exact decimal tokens and a common positive radius. It translates both coordinates by `+1/2` into `[0,1]^2`, with no radius rescaling. The source's wall convention is visible in its [frozen checker](https://github.com/0100001001101111/aletheia-packing-records/blob/d137d44c6eec540b98909231d0e902f0fe4b9b1e/verifier/exact_checker.py#L125); that code was read, never executed.

Let `q=10^24`, `W` be the minimum scaled wall clearance and `D` the minimum squared pair distance of the integer coordinates. For a finer decimal grid with `p>=24`, set `k=10^(p-24)`. The largest feasible integer radius on that grid is

```text
R_p = min(W*k, isqrt(D*k*k)//2).
```

The helper calculates this at p=24 and p=101. Native verification accepts both radii and rejects the next grid unit. Therefore the exact radius limit of these fixed centers lies in `[R_101/10^101, (R_101+1)/10^101)`. Every local working radius exceeds that strict upper bound. An additional exact cross-multiplied squared-distance inequality confirms the ordering without evaluating a square root as a decimal.

For each target, a separate centered `Fraction` calculation agrees with the integer minimum wall and squared pair distance. The three files contain 743,950 unordered pairs per geometry pass. Native verification checks three positive external radii per target (row radius, 24-place maximum and 101-place public radius), plus the local working certificate. The independent rational pass and the integer minimum pass each visit every external pair. Source report integer minima and safe 24-place values agree with the recomputation.

All 28 negative controls reject: next grid units at both precisions, wrong expected N, untranslated centered coordinates, changed source bytes, missing rows, index mismatch, nonfinite decimal token, inconsistent row radius, and the already-retracted N800 display. The last item reproduces the source's own [rounding correction](https://github.com/0100001001101111/aletheia-packing-records/blob/d137d44c6eec540b98909231d0e902f0fe4b9b1e/CORRECTION_2026-08-31_V1.md); it is not a new defect discovery. Base offline reproduction passed 50 certificates/12 frontier rows, all 12 working-start bindings passed, and all 20 existing tests passed in the pinned environment.

## Source access, dates and N500

[SOURCES.md](SOURCES.md) records the discovery route, source dates, retrieval times, authorship, byte hashes and limits. Following the lab's public repository links and owner index exposed the packing archive, which was absent from the previously inspected claim/registry pages. The source commit is `d137d44c6eec540b98909231d0e902f0fe4b9b1e`; all three coordinate Git blob IDs also match its earliest listed commit. [source-manifest.json](source-manifest.json) pins all 14 retained data/report/document files by URL, size, SHA-256 and Git blob ID.

Git author/committer dates are author-controlled, and repository creation does not establish first public availability. The reported 31-August submission is the claimant's statement, not a maintainer-authored receipt. The source describes these as unaccepted candidates. Its proposed license is conditional on owner approval; no approval was established here. The raw files were retained outside this contribution checkout. This PR publishes our code, computed results, links and hashes, without redistributing external coordinates, reports or code.

[N500-SOURCES.md](N500-SOURCES.md) follows a separate source domain. ZeroThesis's [large-N evaluation log](https://zerothesis.com/api/submissions/8f867790aaecd4e33fc3d80cad1224808225274a042801f1f1ee761ff7074976/log) reports an N500 radius of `0.023218395644`, below its displayed reference and this base's working radius. That is an ordering of reported numbers, not an exact geometry check. The inspected public files contain a solver without a stored N500 output. No external solver was run. The relevant Packomania pending range does not disclose per-count membership or a coordinate file. An attributable numerical N500 witness or explicit per-count catalogue disposition is still required; an aggregate score, range or solver source is insufficient.

The final [constructor-archive check](PACKNTILE-SOURCES.md) follows the actual Packntile reference [26]. Its inspected contest pages have no N500 square-circle entry; an N500 sphere entry concerns another objective and was excluded. Redirected/missing archive endpoints yielded no additional numerical witness. The note records the exact links, hashes, date limits and unchecked archive branches; it makes no claim of exhaustive absence.

## Replay

Use an authorized local capture of the public source repository at the pinned commit, preserving relative paths. The 14 required URLs and hashes are in the manifest. Do not run the external repository's code. With this contribution checkout and those local data/document files:

```sh
python3 research/reconciliation-20261023/compare.py --source-dir /path/to/aletheia-packing-records --output /tmp/reconciliation.json
```

Only the standard library and this repository's exact verifier are used. The saved run used Python 3.12.11. Run with assertions enabled; the helper rejects optimized Python invocation. It writes a computed report, never a normalized coordinate file, and makes no network request. All source bytes must match their pins before parsing. Replays must also use the unchanged working-start index bound in the report. Exact values and hashes should reproduce; Python description and elapsed seconds may differ.

## Limits and credit

This is author-checked AI assistance, including three background primary-source research rounds under the same donor session. Separate agents and arithmetic implementations do not establish independent review. No external solver execution, search history, unbounded input format, first-publication/receipt proof, comprehensive pending-candidate search, licence-approval determination, global optimum or scientific acceptance was checked. The unavailable 317-attempt continuation-study archive is a different handoff.

Credit for the external files remains with Bo Brothers / Project Aletheia as their sources state. Credit for the local constructions remains with Eckard Specht at N=600/700/800 and the earlier pilot/contributor refinements, and with the Packntile team for the retained N500 working start. The preceding audit at commit `c355f7681bc0ce1622a5f3cf3ffd46f70108ac01` supplied the question and preserved its earlier access limits. No witness, working-start index, historical package, frontier or accepted-result record was changed.
