# Initial pilot result package

The original 12-count local pilot is documented in [REPORT.md](../../REPORT.md), with [source-backed records](../../RECORDS.md), [source audit](../../AUDIT.md) and [validation receipt](VALIDATION.md). It found two catalogue-baseline improvements, with novelty unresolved. Its frozen trial evidence is under ../../experiments/stage1 and ../../experiments/continuation.

Run `python3 src/reproduce.py --all-trials` from the project root. VERIFY.json describes the check; TASK.json records scope and remaining questions. Original construction authors retain credit in ../../data/records.json; code, audit and experiments were assembled by an OpenAI coding agent. No independent human review or maintainer acceptance occurred.

## Open next questions

- **Question:** Are the improvements unclaimed? **Why:** Catalogue gains do not establish novelty. **First step:** `python3 src/project_inspect.py audit`. **Blocked by:** Accessible pending witnesses and independent review.
- **Question:** Do stronger starts leave short-session headroom? **Why:** Donors need sustained progress. **First step:** Read [the subsequent contributor test](../contributor-20261020/README.md). **Blocked by:** Nothing for already authorized local work; broader donor yield is unmeasured.

This index was added during the follow-up packaging audit; it does not retroactively change the original run.
