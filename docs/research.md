# Research and differentiation

Research reviewed on 2026-08-16. These primary sources informed the benchmark contract. No source code, benchmark samples, climate measurements, or source records were copied.

## Primary sources

| Source | What informed this project |
|---|---|
| [GHG Protocol Standards and Guidance](https://ghgprotocol.org/standards-guidance) | Climate answers need explicit accounting context; a plausible number without the correct organizational/entity boundary is not enough. |
| [NIST SP 811: Guide for the Use of SI](https://www.nist.gov/publications/guide-use-international-system-units-si) | Quantities and units should be explicit and conversions should use a reviewed allow-list rather than heuristic string matching. |
| [W3C PROV-O Recommendation](https://www.w3.org/TR/prov-o/) | Evidence should carry source identity and validity context so provenance can be exchanged and inspected. |
| [OpenAI Evals](https://github.com/openai/evals) and its [JSONL eval guidance](https://github.com/openai/evals/blob/main/docs/build-eval.md) | Line-oriented, versioned examples and adapter boundaries make evaluation datasets reviewable and tool-independent. |

## Deliberate differentiation

Climate Evidence Bench does not grade prose style or ask a model to judge another model. It deterministically evaluates a structured claim:

- numeric tolerance is applied only after an explicit same-dimension unit conversion;
- year, geography, and entity are independent components rather than text-similarity hints;
- citations must name an accepted source and pass publication/valid-from/valid-until checks at an as-of date;
- failures use stable machine-readable codes while scores retain component visibility;
- tasks and answers are JSONL, so provider/model adapters stay outside the evaluator.

The benchmark does not establish that an accepted source is scientifically correct. Source admission is a dataset-governance responsibility; this tool tests whether an answer uses the admitted evidence in the requested context.

## Data boundary

Every bundled prompt, entity, geography, value, year, URI, and citation is synthetic. The primary sources above motivate evaluator design only and are not evidence for any demo answer.
