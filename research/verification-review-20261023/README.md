# Cross-runtime review of the rational certificate audit

This package takes up the [open verification handoff](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19129874)
for [PR 8](https://github.com/discoveryathome/circle-packing/pull/8), pinned at
`b01a3aea620366ec693adfb83bbd6d286dff73c7`. The question is whether its Fraction
oracle, finite domain, and saved provenance support its bounded geometry conclusion.
The session base is `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a`;
seed `c68557875f8ed1f9b2d61ce46a7dc42e` drew `verification / verify-adversarial`.
The [claim](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19139225)
declared the scope before new computation. This is AI-assisted, **author-checked**
evidence. A different runtime and a fresh session do not establish independent
scientific review, novelty, or acceptance.

## Reproduce

The review needs Python 3.10+, its standard library, and Node.js with BigInt support
(tested versions are recorded in the results). No numerical environment, package
installation, or solver is needed. Obtain a separate, immutable checkout of PR 8:

```sh
git fetch origin refs/pull/8/head
git worktree add --detach ../rational-pr8 b01a3aea620366ec693adfb83bbd6d286dff73c7
python3 research/verification-review-20261023/review.py --predecessor ../rational-pr8 --output /tmp/packing-verification-review.json
```

Run the commands from this repository's root, with the contribution checked out.
Once the predecessor checkout exists, execution is offline. The script checks the
predecessor's audit, README, saved result, verifier, and working-start index against
fixed SHA-256 values, then reruns its complete audit. All saved fields must match
except Python version and elapsed time. Every indexed witness hash and exact radius
must match too. Modified inputs fail rather than silently defining a new review.
The source hashes, runtime versions, per-grid result digests, and original construction
credits are recorded in the output. Timing is descriptive, not a performance result.

## What was reviewed

The predecessor's normalized Fraction inequalities correspond to the contract for
positive denominators: containment is the conjunction of four disk-extremum wall
inequalities, and disjoint interiors are equivalent to center distance at least twice
the radius. Squaring preserves that comparison because both quantities are nonnegative.
Pairwise checking is sufficient for the supplied circles; it says nothing about the
largest possible radius. Equality permits tangency. A singleton has no pair minimum.

The Fraction oracle intentionally assumes well-formed, nonempty geometry inputs.
Its separate format controls test selected rejections; they do not implement a second
complete parser. Its eight transformed versions of each large working witness use
the production verifier, as its README explicitly states. The saved hashes identify
the inspected code and data; they do not certify historical authorship or novelty.
The full replay compares these declarations with the saved executable evidence.

The additional Node oracle uses arbitrary-precision BigInt arithmetic. It checks
containment using the concentric center square: `abs(2X-Q) <= Q-2R` on both axes.
Its exact wall margin is half the least gap in that inequality. Integer parity makes
this division exact. It computes every squared pair-distance excess independently
of the Python implementation and its parser. It assumes well-formed integer-string
inputs; it is research verification code, not a replacement certificate-loading API.

Each runtime independently enumerates every unordered multiset of N points from
`{0,...,Q}^2`, including duplicates, for N=1,2 with Q=1..12 and N=3 with Q=1..5.
For each, R runs from 1 through `floor(Q/2)+1`. Python uses `itertools`; Node uses
a separate recursive generator. Every per-Q count is checked against
`binomial((Q+1)^2+N-1,N) * (floor(Q/2)+1)`. Permutations are not enumerated.

For each case, a canonical stream records rejection or acceptance with the exact
radius numerator/denominator, wall margin, squared pair margin, and pair count.
The two SHA-256 stream digests must agree for every N,Q row; comparing only aggregate
accept/reject counts would miss offsetting disagreements. The Python side also checks
the returned minimizing pair and reported denominators.

For each of the 12 hash-pinned working starts, both runtimes check the original,
all eight square symmetries combined with reversed labels, and common integer
rescaling by 97. The exact wall and squared pair margins must obey their respective
linear and quadratic scaling rules. Each original is also rejected for requested
counts N-1 and N+1. The index retains the stronger, unaccepted N=500,700,800 proposals.

Thirty-one declared geometry/count controls include oblique tangency, overlap,
separation, duplicates, oversized and zero radii, a negative denominator, and wrong
requested counts. At 16-, 80-, and 200-digit scales they test pair tangency and
one-unit changes, plus a one-unit violation of each wall. These are explicit positive
and negative controls, not just agreement between implementations. The separation
fixtures use radius Q/5 so moving a center outward does not also cross a wall.

## Evidence

The final run in `results.json` reproduced all 14 non-runtime predecessor fields.
Python 3.13.5 and Node v22.23.4 agreed on 306,333 grid cases: 23,375 accepted and
282,958 rejected. All 31 controls (9 positive, 22 negative) agreed. The 12 working
starts contain 1,074,976 pairs; their ten accepted versions require 10,749,760 pair
checks per runtime, with 24 further requested-count rejections. There were zero
disagreements. The final run took 67.421 seconds on this uncontrolled machine;
no speed comparison is claimed.

During validation, deliberate faults in the Node oracle were detected by the
declared controls: replacing `< 0` with `<= 0` failed 9 controls, omitting pair
rejection failed 5, omitting requested-count binding failed 2, and rounding
coordinates through `Number` failed 7. Changing the predecessor result file by
one byte was rejected by its pinned hash before replay. These are scoped failure
controls, not additional coverage of all possible defects.

The result remains scoped to the enumerated domain and saved witnesses.
The project's eight original verifier tests and baseline reproduction (50 certificates,
12 frontier rows) passed before this work. The initial environment lacked NumPy.
During the continued donation, a private Python 3.12.11 environment was installed
with the exact project requirements, and all **20 tests** passed, including the two
optimizer tests. This closes that initial validation gap; the saved audit remains
the original frozen-source run.
Production verification, construction data,
working starts, and accepted-result records are not modified by this package.

## Open next questions and limits

- A reviewer can inspect the two enumeration algorithms, the concentric-square wall
  identity, the canonical stream format, and the pinned replay. A separate implementation
  is still not a separate reviewer; no independent human signoff is claimed.
- Arbitrary N,Q, all encodings, JSON parser equivalence, file/resource limits, and all
  point permutations were not exhausted. Node consumes well-formed geometry data only.
- The certifier's coordinate rounding and maximal integer radius on its fixed grid
  remain a separate verification question. Start with `src/certify.py` and compare its
  emitted radius to exact wall caps and integer square-root pair caps, with a radius+1
  rejection control.
- Solver correctness, numerical search productivity, external records, pending claims,
  global optimality, and the serial-study package retained in an earlier donor workspace
  were not checked. No new packing or accepted result is proposed.

## Predecessor and construction credit

PR 8's Python Fraction audit and its mathematical explanation were authored by the
preceding OpenAI coding-agent session, posted by `thakrarsagar`. This session reviews
that work and adds cross-runtime evidence; it does not claim its audit or constructions
as new. The original pilot supplied the production verifier and certificate contract.

Construction credit stays with the authors in `discover/working-starts.json`, copied
unaltered into the results: Bernardetta Addis, Marco Locatelli, Fabio Schoen; Xiangjing
Lai, Jin-Kao Hao, Renbin Xiao, Fred Glover; Wenqi Huang, Tao Ye, David W. Cantrell;
Packomania reference [25]; the Packntile team (reference [26]); and Eckard Specht.
Existing pilot and contributor refinements retain their parent credit. This package
adds verification and documentation only, with no automatic coauthorship claim.
