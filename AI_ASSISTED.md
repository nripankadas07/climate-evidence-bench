# AI-assisted development disclosure

OpenAI Codex assisted with research synthesis, evaluator decomposition, implementation scaffolding, documentation drafting, and adversarial test generation for the initial `0.1.0` release.

Human review remains required. The maintainer owns task/source admission, scoring choices, license review, taxonomy governance, and every claim made about benchmark results. AI-generated changes are treated as untrusted until tests and an appropriate domain review are complete.

## Verification performed for 0.1.0

- unit conversion and dimension-mismatch tests;
- tolerance, entity, geography, year, citation, and temporal-validity failures;
- malformed schema, missing answer, duplicate/orphan reporting, and JSONL integration tests;
- strict JSON serialization and byte-for-byte golden artifact comparison;
- Python 3.9 grammar, wheel-build, install, and console-script smoke tests.

No external benchmark code, measurements, or source records were copied. The runtime makes no model or network calls, and every bundled claim is visibly synthetic.
