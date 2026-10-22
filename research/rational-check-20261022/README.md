# Exact rational cross-check of packing certificates

At base `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a`, a separately written
`fractions.Fraction` calculation agreed with `src/verify.py` on **306,333 small-grid
configurations** and all **12 current working starts**. No geometry or reported-margin
disagreement was found in this bounded check. This is **author-checked** research
assistance by an OpenAI coding agent, not independent scientific review or acceptance.

The package adds evidence for the `verify-adversarial` catalogue card. It does not
change the verifier, any construction, the working-start index, or the formal frontier.
The original construction credits and source links are retained in each working-start
entry of [results.json](results.json).

## Reproduce

Python 3.10+ and the standard library are sufficient; no solver, installation, network,
or external service is needed. From the repository root:

```sh
python3 research/rational-check-20261022/audit.py --output /tmp/packing-rational-check.json
```

The script also works from another directory. Do not use `-O`; the audit rejects it
because its checks use assertions. A disagreement exits unsuccessfully and identifies
the case. Progress goes to stderr. The saved run used Python 3.13.5 and took 44.306
seconds on the donation machine; this uncontrolled duration is not a performance claim.
The output pins the audit, production verifier and working-start index by SHA-256,
and checks each witness against its indexed hash before testing geometry.

Before this audit, the project's eight verifier tests passed, and `python3
src/reproduce.py` reported 50 certificates and 12 frontier rows passing. Those original
checks are separate from the new rational cross-check.

## Frozen domain and observations

For each listed N,Q, enumerate every unordered multiset of N points from
`{0,...,Q}^2`, including duplicate centers, and every integer radius numerator
`R=1,...,floor(Q/2)+1`. Coordinates and radii are normalized by Q. Oversized radii,
wall contacts and violations, overlaps, and tangencies consequently occur in the
enumeration. Permutations of each multiset are not separately enumerated.

| N | Q range | Configurations | Accepted | Rejected |
|---:|---:|---:|---:|---:|
| 1 | 1–12 | 4,367 | 1,001 | 3,366 |
| 2 | 1–12 | 265,901 | 22,226 | 243,675 |
| 3 | 1–5 | 36,065 | 148 | 35,917 |
| Total | | 306,333 | 23,375 | 282,958 |

The number of point multisets for a fixed N,Q is
`binomial((Q+1)^2 + N - 1, N)`. The full per-Q accounting is saved in the results.

Sixteen additional geometric controls cover the maximal singleton, oblique 6–8–10
tangency and nearby separations, a prime denominator, duplicates, all four walls,
and tangency versus one-unit overlap with denominators of 16, 80 and 200 digits.
Twenty format/count controls reject selected malformed encodings and wrong requested
counts. These controls have explicitly stated expected outcomes; they are not just
agreement between two implementations.

The twelve working starts, N in {100,106,134,150,200,250,300,400,500,600,700,800},
passed normalized rational containment and all **1,074,976 unordered pair checks**.
For accepted cases the audit also compares the reported radius, minimum wall slack,
minimum squared pair slack, a returned minimizing pair and the number of checked
pairs. In addition, the production verifier preserved the expected margins under
all eight square symmetries combined with reversed circle labels, and under common
integer rescaling by 97. Each working start was rejected under requested counts N−1
and N+1. These transformations use exact geometry invariance; they do not rerun the
rational pair loop for every transformed large witness.

The working starts at N=500,700,800 are the newer contributor proposals. The other
nine use the recorded frontier certificates. Passing their checks does not promote
those proposals to the formal frontier.

## Why the geometry checks correspond

For positive Q,R, write `x=X/Q`, `y=Y/Q`, `r=R/Q`. A closed radius-r disk lies inside
the unit square exactly when its four coordinate extrema do, namely
`r <= x,y <= 1-r`. Multiplication by positive Q gives the integer wall inequalities
in [the pinned contract](https://github.com/discoveryathome/circle-packing/blob/978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a/METHODS.md).

Two disks have disjoint interiors exactly when their center distance is at least
`2r`: a smaller distance places their midpoint in both interiors, while a shared
interior point would force a smaller distance by the triangle inequality. Squaring
nonnegative quantities and multiplying by positive `Q^2` yields the contract's
integer pair inequality. Equality allows tangency. Checking every pair therefore
establishes feasibility of this supplied rational construction, not optimality.

The new oracle constructs fractions directly from integers and operates in normalized
coordinates; it does not call the production integer parser or geometric predicates.
It intentionally assumes well-formed, nonempty, positive-denominator geometry inputs.
Malformed representation checks are the separate finite controls above, not a second
complete schema parser. Both implementations still depend on Python's integer
arithmetic. Separate code and mathematical source-reading assistance do not amount to
an independent reviewer.

Pair slack is a **difference of squared distances**, not linear clearance. For a
singleton there are no pairs, so the pair minimum and minimizing pair must be absent.
Equivalent fraction spellings are compared by rational value, not as strings.

## Scope and open next questions

- This is finite agreement evidence, not exhaustive testing over arbitrary N, Q or
  encodings, and not a proof that the software is defect-free.
- File parsing/resource limits and all possible malformed JSON shapes were not
  exhaustively checked. The new differential calls target `verify`, while the original
  reproduction command exercises saved-file loading separately.
- No solver run, new construction, external-record comparison, pending-claim
  reconciliation, global-optimality argument or novelty claim was made.
- A reviewer can rerun the script, inspect its oracle and source hashes, and judge
  the stated mathematical equivalence separately from finite implementation coverage.
  A different-language implementation would reduce shared-runtime dependence.
- The certifier's rounding and fixed-grid maximal-radius behavior is a separate
  follow-up; this package checks the emitted geometric certificates.

The project and card were selected by the hub's seeded rules. Donation seed:
`4f662e5be88de40a92015b3765b913e8`; round-2 seed:
`db3fcbb737f3095b0d122f377d40c7d1`. The scope was frozen before enumeration. The
[coordination claim](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19129610)
records the task. Evidence and acceptance distinctions follow the
[pinned working-start index](https://github.com/discoveryathome/circle-packing/blob/978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a/discover/working-starts.json)
and [review brief](https://github.com/discoveryathome/circle-packing/blob/978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a/research/readiness-20261021/REVIEW.md).
