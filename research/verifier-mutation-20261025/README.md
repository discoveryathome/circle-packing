# Mutation analysis of the verifier's regression suite

At base `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a`, 63 of 177 single-point faults in
`integer()` and `verify()` pass `tests/test_verifier.py`, and **39 of those change an
accept/reject decision**. Among them: dropping the bottom, right or top wall check, accepting
`"+4"`, `"04"` or `"4 "` as integers, skipping the schema check, and accepting a centre
written as the string `"11"`. A verifier carrying any one of these regressions still passes
all eight tests. The new `tests/test_verifier_faults.py` (29 witnesses plus one report
check) kills **38 of the 39**, plus one limit fault and eight of nine report-only faults.
The remaining one needs a Python tuple, which no JSON certificate can produce.

No defect was found in `src/verify.py` itself: on a deterministic corpus of 32,563
certificates, its decisions match a separate oracle in every case. The oracle's geometry is
written from METHODS.md; its input-format limits are copied from `verify.py`, so agreement
on those is not independent. This is **author-checked** work by an AI coding agent (Claude Opus 5.5, Anthropic)
operated by [@VibeCodyH](https://github.com/VibeCodyH). It is not
independent review or acceptance. `src/verify.py`, every construction, the working-start
index and the formal frontier are unchanged.

## Reproduce

Python 3.10+ and the standard library. From the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_verifier*.py'
python3 research/verifier-mutation-20261025/check_witnesses.py
```

The first runs the old and new verifier tests. The repository README's quick check uses
`-p test_verifier.py`, which skips the new file. The second command re-derives the expected
outcome of every new witness with `spec_oracle.py` and recomputes the report minima.
Loading the witness file imports `src/verify.py`, but the check never calls it.

To replay the mutation analysis, set `OUT` to an absolute folder **outside** the checkout:

```sh
python3 research/verifier-mutation-20261025/mutate.py --out "$OUT/base" --bwrap \
    --suite test_verifier.py --suite test_packing_task.py
bwrap --ro-bind / / --tmpfs "$HOME" --ro-bind "$PWD" "$PWD" --bind "$OUT" "$OUT" --tmpfs /tmp \
    --dev /dev --proc /proc --unshare-net --die-with-parent --chdir "$PWD" \
    python3 -I -B research/verifier-mutation-20261025/classify.py \
    "$OUT/base/kill-matrix.json" "$OUT/base/mutants" --out "$OUT/base/classification.json"
python3 research/verifier-mutation-20261025/mutate.py --out "$OUT/extended" --bwrap \
    --suite test_verifier_faults.py --suite 'test_verifier*.py'
```

`mutate.py` copies the checkout (without `.git`) into `$OUT`, rewrites only the copy's
`src/verify.py` for each mutant and runs each suite with `python3 -I -B`. A failing or
timed-out suite counts as a kill; no run timed out. `--bwrap` runs each suite under
bubblewrap with no network and the home folder hidden; without it, mutants run
unsandboxed. `classify.py` executes mutated code, hence the `bwrap` line. Mutant numbering
is deterministic for the `verify.py` and harness hashes recorded in each JSON file and a
given Python version (`ast.unparse` output can differ between versions; the saved runs
used 3.12.3). The harness stops if the unmodified control is killed or the always-accept
control survives.

Saved outputs from that replay: [kill-matrix-base.json](kill-matrix-base.json),
[classification-base.json](classification-base.json),
[kill-matrix-extended.json](kill-matrix-extended.json) and
[witnesses.json](witnesses.json) (the `check_witnesses.py` result). Mutant sources are
not saved; the harness regenerates them.

## Method

The operator set was declared before the first run: relational-operator replacement
(boundary and negation), `and`/`or` swap, boolean-operand deletion, `not` removal,
integer constant ±1, five regex variants plus `re.fullmatch` → `re.match`/`re.search`,
arithmetic-operator replacement, binary-operand deletion, argument deletion in `min()`,
`range()` bound ±1, guard removal (`if` test → `False`), statement deletion, and the exact
type test → `isinstance`. Only `integer()` and `verify()` are mutated; `load_verify()`
(PR 11) and `certify.py` (PR 10) are out of scope. Syntax-invalid and duplicate mutants are
discarded, leaving 177.

Two controls run first in every matrix: the unmodified source after an AST round trip (must
pass every suite) and a hand-written `verify()` that accepts without checking anything
(must fail every suite). Both behaved as required in all runs.

`classify.py` runs the unmodified verifier, each surviving mutant and `spec_oracle.accepts()`
over one corpus: field-level variants of three small certificates (schema, count, requested
count, integer spellings, centre shapes, 199/200/201-character scalings), every one- and
two-circle placement with Q ≤ 4, 1 ≤ R ≤ Q and coordinates in `[-1, Q+1]`, every
three-circle placement with Q ∈ {2, 3}, 1 ≤ R ≤ Q and coordinates in `[0, Q]`, 3,000 seeded
near-contact random cases, and the N=100 working start
with ±1 moves of eight centres. A mutant is a **decision** fault if it decides some case
differently from the oracle while the unmodified verifier agrees with it, **report-only**
if decisions always agree but an accepted report differs, and **no difference** otherwise.

The oracle (`spec_oracle.py`) takes its geometry from METHODS.md, "Rigorous
feasible-coordinate certificate", using normalized `Fraction`s. The input limits
(1 ≤ N ≤ 10,000; canonical ASCII decimal strings of at most 200 characters) are not in
METHODS.md, so the oracle takes them from `src/verify.py`; that part is not independent.

## Results

Base suites against 177 mutants: `test_verifier.py` kills 114. `test_packing_task.py`, which
also calls `verify()`, kills only one of the remaining 63 (M132). The 63 survivors of
`test_verifier.py` classify as 39 decision faults, 9 report-only and 15 with no difference.
The unmodified verifier agreed with the oracle on all 32,563 corpus cases (1,045 accepted).

| What the surviving fault does | Decision faults | Killed after adding `test_verifier_faults.py` |
| --- | ---: | ---: |
| Skips or miscomputes the bottom, right or top wall check, so a circle crossing that side is accepted | 16 | 16 |
| `2*r > q` becomes `2+r > q`, rejecting the single radius-1/2 circle at Q = 2 (M060) | 1 | 1 |
| `(x-u)**2` becomes `(x-u)**3`, rejecting a valid tangent pair when the later circle is to the left (M132) | 1 | 1 |
| Accepts `"+4"`, `"04"`, `"4 "`, `"1\n"` or `"\u0664"`, or moves the 200-character limit by one | 10 | 10 |
| Skips the schema check, or accepts N given as `4.0`, `true` or `0` | 7 | 7 |
| Accepts a centre written as the string `"11"` or an object with two keys | 3 | 3 |
| Accepts a Python tuple of centres (M067; JSON cannot produce one, see below) | 1 | 0 |
| **Total** | **39** | **38** |

The new suite also kills M035 (N = 10,001 accepted; one of the three limit faults with no
corpus difference) and 8 of the 9 report-only faults, which corrupt the reported wall slack,
pair slack, slack denominator or closest pair without changing a decision.

With `test_verifier*.py` (old and new tests together), 16 of 177 mutants survive: the 13
listed as equivalent below and the 3 described under "Survivors that remain". The controls
behaved as required in both matrices.

## Survivors that are equivalent

Twelve of these showed no difference on the corpus. Each has a short argument that no input
can distinguish it; M067 holds for JSON-decoded input only:

| Mutant | Change | Why the decision cannot change |
| --- | --- | --- |
| M010 | regex drops `-?` | A negative Q or R is rejected by the scale guard. A negative coordinate gives `x - r < 0` because R ≥ 1. Only the error message changes. |
| M012 | regex rejects `"0"` | Q = 0 and R = 0 are rejected by the scale guard. A zero coordinate gives `x - r < 0`. |
| M047, M050, M052, M053 | `q <= 0` dropped, or `q < 0`, `q <= 1`, `q <= -1` | Each differs only for Q ≤ 1 with R ≥ 1, where `2*r > q` already rejects. |
| M049, M061, M062, M064 | `2*r > q` dropped, or `2 > q`, `r > q`, `1*r > q` | N ≥ 1 is checked first, and the first centre's wall check needs R ≤ X ≤ Q − R, so 2R > Q is rejected there. `2 > q` additionally rejects only Q ≤ 1, which is rejected anyway. |
| M076 | `len(p) != 2` dropped | A centre list of any other length fails `x, y = [...]` with `ValueError`, or `integer()` raises first. |
| M153 | `slack < 0` → `slack < -1` | `slack = dx² + dy² − 4R² ≡ dx² + dy² (mod 4)`, which is 0, 1 or 2, so `slack = −1` never occurs. |
| M067 | `isinstance(c['centers'], list)` dropped | Equivalent for JSON-decoded input only. A JSON string or object of length N iterates as N strings, which the per-centre list check rejects. A Python tuple of lists is accepted, which is why the corpus reports a decision difference. |

## Survivors that remain

- **M031, M036** (`n < 10000`, `n <= 9999`) reject a valid 10,000-circle certificate. A test
  that kills them must verify one, which costs 49,995,000 pair checks on every suite run. Not
  added; the largest frontier count is 800.
- **M159** (`slack < min_pair` → `<=`) reports the last of several equally tight pairs
  instead of the first. The report does not define a tie-break, so no test pins it.

## Harness defect found and fixed

The first full run reported M008 (`re.fullmatch` → `re.match`) as killed. It was not: M007
and M008 have the same source length and were written within the same second, so Python
loaded M007's cached bytecode for M008. Two other outcomes (M148, M157) were affected the
same way. The harness now runs every suite with `-B`, copies no `__pycache__`, and stops if a
bytecode cache appears. All numbers above come from the corrected runs.

## Not checked

- `load_verify()`, file reading and JSON decoding (PR 11), `certify.py` (PR 10), the
  session layer in `src/packing_task.py` (PR 14) and the CLI's exception mapping.
- Faults outside the declared operators, and combinations of two or more faults.
- The corpus is finite; "no difference" is a statement about it, backed by the arguments
  above, not an exhaustive search.
- Integer overflow: Python integers are arbitrary precision. The 200-character cap keeps
  every input integer below 10^200 in magnitude, so squared terms stay below about 10^401;
  fixed-width overflow cannot occur in `verify.py`. Other
  implementations (for example PR 9's Node BigInt check) were not re-examined.
- Same-session tooling wrote the oracle and the tests. Agreement between them is not an
  independent review.

## Open next questions

- Should the suite also pin acceptance at N = 10,000 (M031, M036), and should both input
  limits (N ≤ 10,000, 200 characters) move into METHODS.md as part of the contract?
- Should the repository README's quick check use `-p 'test_verifier*.py'`?
- The same harness can be pointed at `certify.py` or `load_verify()` once PRs 10 and 11
  are settled: does `tests/` catch faults in the certificate builder?

## Credit

The verifier and its original tests are the pilot implementation credited in
CONTRIBUTORS.md. The witness style follows those tests. PR 8's rational audit and PR 9's
BigInt cross-check (both open) already include wall, overlap and format controls, but they
live in `research/` and only run when someone invokes them. This package puts witnesses in
`tests/`, where `python3 -m unittest discover -s tests` runs them. Task drawn with seed `945e64a2261933eff4beebe8f6e7088b` (track `verification`,
card `verify-adversarial`); claim:
[discussioncomment-19175399](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19175399).
