# Architecture

The benchmark deliberately separates provider adapters from evaluation:

- `io.py` reads and writes line-delimited JSON without provider assumptions.
- `units.py` owns a small, inspectable dimensional registry.
- `evaluator.py` validates task boundaries and runs seven independent components.
- `demo.py` supplies synthetic fixtures that exercise both passes and failures.
- `reporting.py` renders one stable result artifact in three formats.

## Evaluation order

1. Validate nested task schema, finite tolerance bounds, exact calendar-valid `YYYY-MM-DD` source dates, coherent publication/validity intervals, and unique task/answer identifiers.
2. Match answer by `task_id`.
3. Convert numeric value through an explicit spelling allow-list that preserves dimensional operators. A precomputed factor ratio prevents avoidable intermediate overflow/underflow, and equal-factor aliases preserve the finite input exactly. Apply exactly `max(absolute, relative)` tolerance with no undeclared epsilon.
4. Compare year, normalized geography, and normalized entity.
5. Match at least one accepted source.
6. Confirm its publication and validity interval against `evaluation_as_of`.
7. Apply documented component weights and emit failure codes.

The evaluator does not use an LLM judge. This keeps results deterministic, inexpensive, auditable, and suitable as a low-level contract beneath qualitative review. A non-finite converted value fails the numeric component but does not suppress independent year, geography, entity, citation, or temporal-validity evaluation.

## Schema policy

Tasks, answers, and reports currently use `1.0.0`. Additive fields may be introduced within `1.x`; semantic changes to existing fields or scoring require a major schema revision.
