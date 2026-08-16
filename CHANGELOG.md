# Changelog

## 0.1.1 - 2026-08-16

- Reject arbitrarily large task numbers as controlled validation errors instead of leaking `OverflowError` tracebacks from the evaluation CLI.
- Classify arbitrarily large answer numbers as `invalid_numeric` findings and continue producing a reviewable report.
- Add evaluator and subprocess regressions for both oversized-number trust paths.
- Compute unit conversions with a precomputed factor ratio, preserving exact identities at finite extremes and preventing intermediate overflow or underflow from changing pass/fail outcomes.
- Continue independent context and citation scoring after a converted value becomes non-finite.
- Publish reports and optional demo JSONL through one staged, symlink-safe bundle writer that restores the complete prior set after a mid-commit failure.
- Serialize cooperating report writers with an exclusive advisory lock on the verified output directory, recheck target identities immediately before publication, and reconcile rename outcomes before rollback when a filesystem wrapper raises after completing the operation.
- Close fallback temporary descriptors when text-stream setup fails, while removing the abandoned staged file.
- Ship examples, golden artifacts, documentation, and the release checker in the source distribution; CI now extracts the sdist and reruns its full suite on Python 3.9 and 3.12.
- Migrate package license metadata to the SPDX form.

## 0.1.0 - 2026-08-16

- Replace heuristic unit punctuation stripping with an explicit alias allow-list that preserves dimensional operators.
- Validate finite tolerance bounds, nested expected/source fields, and malformed nested answers deterministically.
- Reject empty task sets and duplicate task or answer IDs with stable CLI errors.
- Neutralize untrusted text in Markdown reports.
- Remove the undeclared absolute comparison epsilon so only task tolerance controls numeric acceptance.
- Require exact calendar-valid `YYYY-MM-DD` dates and reject sources published after their validity end.
- Return CLI status `0` for a full evaluation pass, `1` for valid task findings, and `2` for invalid input or execution errors.
- Initial JSONL task and answer schemas.
- Numeric, unit, context, citation, and temporal evaluation.
- Stable failure taxonomy and weighted scorecard.
- JSON, Markdown, and single-file HTML reports.
