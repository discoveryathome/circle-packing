# Exact certifier rounding and fixed-grid maximality

The certifier's intermediate multiplication in an 80-digit Decimal context can
erase a difference just above or below a half-grid tie. The emitted geometry can
still pass exact verification while its rounded coordinate differs from the
intended half-even result. On a coarse grid it can also reject a valid rounded
singleton. An inherited Decimal exponent limit can make ordinary inputs overflow.

This contribution converts the exact Decimal input to a Fraction before multiplying
and uses exact half-even rounding. The public function, decimal-string conversion,
certificate format, geometry checker, radius-cap calculation, and historical
artifacts are preserved. Original construction/refinement credit is retained.

## Reproduce the defect

At base `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a`:

```python
from certify import make_certificate
x = '0.2500000000000005' + '0'*84 + '1'
c = make_certificate([[x, '0.5']], {})
print(c['centers'][0][0])
```

The original prints `250000000000000`; exact half-even rounding requires
`250000000000001`. This is an error in rounding the supplied coordinates, not an
invalid geometry accepted by `verify.py`. With `x='0.25'+'0'*80+'1'` and scale 2,
the original rounds to the wall and rejects a singleton that should round to (1,1)
with radius numerator 1. A caller's `localcontext().Emax=9` also causes the original
to overflow for ordinary (0.5,0.5) at the default scale.

Five regression tests cover the two directions of near-tie rounding, exact even/odd
ties, the coarse-grid witness, and exponent-context isolation. Before the fix, two
tests failed, two errored, and the exact-tie positive control passed.

## Bounded audit

The [coordination claim](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19139799)
took up the [open certifier handoff](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19139534)
on the original seeded verification track. The domain was frozen before new
computation. The seed is `c68557875f8ed1f9b2d61ce46a7dc42e`.

The oracle parses this audit's fixed-point decimal strings as integer numerator /
power of ten. It rounds using divmod and parity rather than Decimal or Fraction
rounding. After rounding centers, it computes exact wall and pair distances and
finds the largest integer radius by monotone binary search, rather than the
production `isqrt` formula. Every emitted positive witness must pass the expected-N
geometry check, and increasing its radius numerator by one must fail.

The corpus includes:

- All unordered multisets of N=1..4 points from `{0.1,0.3,0.5,0.7,0.9}²` at every
  integer scale Q=2..32, including duplicates: **736,250 configurations**. Per-Q
  counts are checked against the multiset binomial formula. There are 381,367
  feasible rounded configurations and 354,883 rejections.
- N=1, y=0.5, x=m/1000 for m=0..1000 at Q=2..32: **31,031 cases**, with 27,939
  feasible rounded singletons and 3,092 rejections.
- **72** default-scale precision cases: k in {250000000000000,250000000000001,
  499999999999998,499999999999999}, x=(k+1/2)/10^15 + offset*10^-d, y=0.5;
  d in {30,79,80,81,100,200}, offset in {-1,0,1}.
- Three isolated controls: just above/below coarse-grid ties, and an inherited
  Decimal Emax of 9.
- All **12 hash-pinned working starts**, rebuilt from their exact finite-decimal
  center coordinates, with no writes to any stored witness.

The candidate agrees on all **767,368 cases**. The pinned original agrees on the
ordinary grids, scalar cases and working starts, but fails 12 precision cases and
all three isolated controls. The report stores every observed failure (within its
explicit 50-example cap, which is not reached), exact source/witness hashes, per-Q
oracle digests and original construction credits. All 12 stored geometries rebuild
identically under both implementations. No new packing is proposed.

## Replay

Use this contribution checkout and a separate checkout containing the pinned
original certifier, for example PR 8 at
`b01a3aea620366ec693adfb83bbd6d286dff73c7`:

```sh
python3 research/certifier-check-20261023/audit.py --baseline ../predecessor-pr8 --output /tmp/certifier-audit.json
python3 -m unittest discover -s tests -p test_certifier.py -v
```

The audit uses only Python's standard library. The baseline certifier, both
verifiers, working index, and each witness must match fixed SHA-256 values before
use. The baseline failures are required negative controls. The final report is
`results.json`; elapsed time is descriptive and is not a performance comparison.

For numerical caller integration, use the project's pinned Python 3.12 environment:

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 src/reproduce.py
```

The final audit used Python 3.12.11 and took 129.130 seconds on this uncontrolled
machine. All **25 tests** passed in the pinned numerical environment, including the
two optimizer tests; baseline reproduction passed (50 certificates, 12 frontier
rows). The preceding Python 3.13.5 audit found the same finite outcomes. No search
or timing-performance claim follows from these checks.

## Scope, credit, and open next questions

This is **author-checked** AI-assisted work, not independent scientific review.
It follows the preceding OpenAI-agent geometry audits in PRs 8 and 9 and checks a
different step: creation of the rational witness. The original pilot supplied the
certifier and verifier. Construction authors and local refinements remain credited
through the unchanged working index, copied into the results.

The finite agreement does not prove arbitrary-input correctness. Unbounded
precision/resource behavior, all Decimal encodings, solver correctness, external
records, novelty, global packing optimality and scientific acceptance are not
established. The fixed historical serial-study runner deliberately imports its
archived certifier; this change applies to the current certifier and does not
rewrite that frozen study or its prior outputs.

A subsequent verification task can examine the certificate file-loading boundary:
top-level JSON shape, ambiguous keys/constants, bounded reads, and expected-N
binding. Keep such representation checks distinct from the geometry conclusion.
