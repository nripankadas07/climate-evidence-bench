# Climate Evidence Bench report

> **Synthetic benchmark:** Every bundled entity, geography, measurement, and source is synthetic benchmark data. No record is a current climate fact.

- Schema: `1.0.0`
- Tasks: `6`
- Fully passed: `1`
- Pass rate: `16.67%`
- Mean weighted score: `0.767`

## Component pass rates

| Component | Pass rate |
|---|---:|
| Numeric | 66.67% |
| Unit | 83.33% |
| Year | 83.33% |
| Geography | 83.33% |
| Entity | 83.33% |
| Citation | 83.33% |
| Temporal Validity | 66.67% |

## Task results

| Task | Score | Pass | Failures |
|---|---:|:---:|---|
| `unit-conversion-pass` | 1.00 | yes | — |
| `tolerance-fail` | 0.70 | no | numeric_out_of_tolerance |
| `dimension-fail` | 0.60 | no | unit_dimension_mismatch |
| `context-fail` | 0.70 | no | year_mismatch, geography_mismatch, entity_mismatch |
| `source-fail` | 0.70 | no | citation_source_mismatch |
| `temporal-fail` | 0.90 | no | citation_stale |

## Failure taxonomy

- `missing_answer` — No answer record was supplied for the task.
- `malformed_record` — A task or answer is missing a required field or has an invalid type.
- `invalid_numeric` — The answer value is absent, non-numeric, or non-finite.
- `unsupported_unit` — The answer or expected unit is outside the explicit registry.
- `unit_dimension_mismatch` — Answer and expected units describe different dimensions.
- `numeric_out_of_tolerance` — The converted answer is outside absolute and relative tolerance.
- `year_mismatch` — The answer year differs from the requested entity-year context.
- `geography_mismatch` — The answer geography differs after conservative normalization.
- `entity_mismatch` — The answer entity differs after conservative normalization.
- `missing_citation` — The answer includes no citation.
- `citation_source_mismatch` — No cited source is accepted for this task.
- `citation_future_dated` — The selected source was published after the evaluation as-of date.
- `citation_not_yet_valid` — The selected source was not yet valid on the as-of date.
- `citation_stale` — The selected source had expired before the as-of date.

All examples are synthetic and must not be cited as current climate facts.
