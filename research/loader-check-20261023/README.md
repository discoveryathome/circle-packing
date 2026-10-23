# Certificate file-loading boundary

The original loader reads the entire file before enforcing its 10 MB limit.
A non-object JSON value also reaches `.get` and produces an AttributeError;
the standalone CLI then exits without its structured JSON invalid-result output.
This patch limits the initial read to 10,000,001 bytes and rejects oversized input
before decoding, and rejects non-object certificates with ValueError.

The file loader also adopts an explicit unambiguous-JSON policy: duplicate keys
are rejected, including escaped aliases and nested provenance keys, and raw
NaN/Infinity/-Infinity tokens are rejected. This intentionally tightens acceptance
of representations that Python's default decoder accepts. It does not demonstrate
that the original integer geometry checker accepted an invalid geometry.

Python documents these permissive defaults and the decoding hooks used here in
its [JSON interoperability documentation](https://docs.python.org/3.12/library/json.html#standard-compliance-and-interoperability).
[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html#section-4) recommends unique
object names; this loader requires them. The JSON numeric grammar does not include
non-finite constants. Ordinary finite metadata numbers and strings such as "NaN"
remain supported. References checked 2026-10-23; no third-party text is redistributed.

## Scope and frozen controls

The original seed `c68557875f8ed1f9b2d61ce46a7dc42e` drew verification /
verify-adversarial. The [claim](https://github.com/discoveryathome/circle-packing/discussions/2#discussioncomment-19140280)
refined the card to file loading, which the preceding geometry and certifier
audits explicitly excluded. Base: `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a`.

Fifteen adversarial test methods cover:

- Valid file hashes, expected-N binding, ordinary finite provenance, supported
  UTF-8/BOM/UTF-16/UTF-32 byte encodings, and unchanged ordinary geometry behavior.
- Top-level null, booleans, numbers, strings and arrays in both the loader and
  in-memory verifier; the standalone CLI returns nonzero with `valid:false` JSON.
- Empty/trailing/invalid JSON, invalid UTF-8, duplicate geometry keys, an escaped
  key alias and duplicate nested provenance keys.
- Raw non-finite constants versus ordinary strings and finite metadata values.
- Exactly 10,000,000 input bytes, one byte over, and a tracked reader that rejects
  an unbounded request or consumption beyond limit+1.
- Normalization of a decoder RecursionError into ValueError. This is tested by
  failure injection; no fixed JSON nesting limit is introduced or claimed.

The original 14-test boundary set exposed 12 failing assertions and 12 subtest
errors. After the patch all 15 methods pass, including the added decoder-error
control. An initial 2,000-level nesting fixture was supported by both tested
Python runtimes, so it was not treated as an invalid input or a discovered defect.

## Stored-witness compatibility

The replay enumerates the **943 JSON files in the base commit**, selects decoded
objects declaring the equal-circle-square/v1 schema, and checks every selected
file with its stated N through the public file loader. It checks working-start
hash/count bindings separately. This is an audit of a fixed repository corpus,
not a general-purpose scanner for arbitrary untrusted directories.

All **572 stored certificates** pass, covering **83,289,042 exact unordered pairs**.
All **12 current working starts** retain their indexed hashes and counts. The
result contains each checked path, raw SHA-256, radius, count and pair accounting.
Neither coordinates nor historical packages are rewritten.

An additional count-cap control is the ordinary 100x100 square grid at Q=200,
R=1. N=10,000 passes all **49,995,000 pairs**; N=10,001 is rejected by the declared
count limit. This is a software boundary control, not a new packing proposal or
an optimality claim. No new mathematical construction is submitted.

The final replay used Python 3.12.11 and took 65.515 seconds on an uncontrolled
machine. All **35 repository tests** pass in the pinned numerical environment,
including the optimizer tests. Baseline reproduction passes 50 certificates and
12 frontier rows; the full `--all-trials` reproduction passes 234 certificates and
12 rows, including trial-to-count bindings. Timing is descriptive, not a performance
comparison.

## Replay

From this contribution checkout, with the base commit available locally:

```sh
python3 research/loader-check-20261023/audit.py --output /tmp/loader-audit.json
.venv/bin/python -m unittest discover -s tests -v
python3 src/reproduce.py --all-trials
```

The first command needs only the standard library and git. A shallow clone may
need to fetch base `978d4bd925ba4ab62e5ceb2a3b3a108d3e283f1a` first. `results.json`
pins the audit, verifier, working index and every checked witness by SHA-256.

## Limits and credit

This is **author-checked** AI-assisted work, not independent scientific review or
acceptance. The original pilot supplied the verifier and loader; the preceding
OpenAI-agent work in PRs 8–10 established separate bounded geometry/creation
evidence. Original construction/refinement authors remain credited in the unchanged
working index and scientific packages. No record or frontier is promoted.

The geometry formulas, count limits, integer bounds, return shape and raw hashing
of accepted files remain unchanged. Strict representation rejection applies to
`load_verify` and the standalone CLI. Other tools that parse JSON themselves
before calling the in-memory `verify` function were not converted; their lexical
JSON behavior is a separate follow-up.

The raw-byte read limit is not a proof of every decoder allocation, CPU, nesting,
stream or concurrent-file behavior. Untracked/non-JSON archives, all possible
encodings, solver correctness, external records, novelty, global optimality and
scientific acceptance were not checked. A next step can examine consistent use of
the checked file-loading boundary in the candidate-comparison and session tools.
