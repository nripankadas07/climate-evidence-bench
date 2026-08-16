# Changelog

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
