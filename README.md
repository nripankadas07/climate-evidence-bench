# Climate Evidence Bench

Climate Evidence Bench is a dependency-free evaluator for structured climate and sustainability answers. It tests the details that broad text similarity misses: numeric tolerance, unit conversion, year, geography, entity, accepted source, citation presence, and temporal validity.

> **Data boundary:** every bundled entity, geography, measurement, and source is synthetic benchmark data. None is a current climate fact.

## Problem

An answer can contain the right-looking number and still be wrong because it uses tonnes instead of kilotonnes, the wrong reporting year, a neighboring geography, a different entity, an unsupported citation, or an expired source. This benchmark makes each failure independently visible.

## Proof

- Versioned, adapter-friendly JSONL tasks and answers
- Explicit conversion registry for emissions, energy, ratio, area, and volume units
- Absolute plus relative numeric tolerances after conversion
- No hidden comparison epsilon: a zero tolerance means exact equality in the evaluator's floating-point representation.
- Conservative entity/geography normalization
- Accepted-source and as-of-date checks
- Stable failure taxonomy and weighted component scores
- JSON, Markdown, and self-contained HTML from one `1.0.0` result artifact
- Demo JSONL and report bundles are staged and rolled back as a set; cooperating writers hold an exclusive advisory directory lock so their files cannot mix, and output-directory links and pre-existing artifact links are rejected rather than followed.
- Standard-library unit and subprocess integration tests

## 60-second demo

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
climate-evidence-bench demo --emit-jsonl --output-dir reports
open reports/climate_evidence_report.html
```

Evaluate adapter output:

```bash
climate-evidence-bench evaluate \
  --tasks examples/tasks.synthetic.jsonl \
  --answers examples/answers.synthetic.jsonl \
  --output-dir reports
```

`evaluate` returns `0` only when every task passes, `1` when valid inputs produce one or more task failures, and `2` for invalid input or execution errors. Reports are still written for valid evaluation findings. `demo` remains an illustrative taxonomy run and returns `0` after successful execution.

Without installation:

```bash
PYTHONPATH=src python -m climate_evidence_bench demo
```

## Adapter contract

An adapter only needs to produce one answer JSON object per line with the stable schema, `task_id`, numeric `value`, `unit`, `year`, `geography`, `entity`, and `citations[].source_id`. Model and provider code remains outside the evaluator.

## Architecture

```text
task JSONL -----> validator ----+
                                +-> component evaluators -> taxonomy -> score
answer JSONL --> adapter edge --+                              |
                                                        JSON / MD / HTML
```

See [docs/architecture.md](docs/architecture.md) and [docs/limitations.md](docs/limitations.md).

## Release materials

- [Research and differentiation](docs/research.md)
- [Roadmap](ROADMAP.md)
- [AI-assisted development disclosure](AI_ASSISTED.md)
- [Citation metadata](CITATION.cff)
- Golden demo: [HTML](artifacts/demo/climate_evidence_report.html), [Markdown](artifacts/demo/climate_evidence_report.md), [JSON](artifacts/demo/climate_evidence_report.json), [tasks JSONL](artifacts/demo/tasks.synthetic.jsonl), [answers JSONL](artifacts/demo/answers.synthetic.jsonl)

## Limits

The benchmark evaluates structured records, not free-form scientific reasoning or the truth of an external source. Its converter is intentionally allow-listed, text normalization is conservative, and the bundled examples are synthetic fixtures rather than claims about the world. See [docs/limitations.md](docs/limitations.md) for known boundaries and extension points.

## Development

```bash
make test
make demo
make golden
python -m pip install build==1.4.4
release_dir="$(mktemp -d)"
python -m build --sdist --outdir "$release_dir"
python scripts/check_sdist.py "$release_dir"/*.tar.gz
```

The source-distribution check rejects unsafe or cache/build entries, verifies that examples and golden fixtures are present, extracts the archive, and runs its complete embedded test suite.

MIT licensed.
