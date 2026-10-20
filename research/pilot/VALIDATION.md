# Validation receipt

- Exact geometry: 234 stored certificates checked, including all 184 trial outputs,
  37 baseline witnesses, the external N=47 witness and 12 local frontier witnesses.
  `experiments/verification.json` reports 18.775 seconds; all passed.
- Fresh local clone: standard-library verifier passed at the commit recorded in
  `experiments/fresh-clone-verification.txt`, in 7.911 seconds. No network or optimizer.
- Ten unit/integration tests passed, including eight verifier tests.
- Upstream JSON schemas, catalogue weights/IDs/paths, the handoff schema and all four
  task first steps passed. The seeded picker was exercised with
  0123456789abcdef0123456789abcdef and chose verify-adversarial.
- All 12 frontier SVGs have the correct circle count and common radius; rendered
  N=100,600,700 examples were visually inspected. No clipping or legibility issue found.
- Separate source code snapshots for both experiment stages match their recorded hashes.
- A diagnostic command was renamed from inspect.py to project_inspect.py after packaging
  checks exposed a collision with the Python standard library. Protocol and verification
  checks were rerun after the fix. This did not change the completed numerical runs.

These are author checks, not independent human review, proof of optimality, or external
record acceptance. See REPORT.md for the bounded experiment and uncertainty limits.
