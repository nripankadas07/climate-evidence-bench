# Roadmap

Climate Evidence Bench is at `0.1.1`: a deterministic structured evaluator with synthetic fixtures and a versioned failure taxonomy.

## 0.2 — Contract hardening

- publish standalone JSON Schemas for tasks, answers, sources, and reports;
- stable error records for malformed tasks as well as malformed answers;
- scoring profiles and per-task weight overrides with explicit versioning;
- conformance fixtures for third-party adapters.

Exit criterion: an adapter can validate locally before submitting answers, and every rejection is machine-readable.

## 0.3 — Evidence depth

- citation spans and claim-to-source alignment fields;
- derived-value tasks with transparent calculation traces;
- source snapshot hashes and richer provenance metadata;
- benchmark slice reports by dimension, geography, year, and failure family.

Exit criterion: evaluators can distinguish a wrong source, a wrong extraction, and a wrong calculation.

## 1.0 — Governed benchmark releases

- immutable dataset release manifests and migration policy;
- leakage review, independent task review, and adapter reproducibility guidance;
- uncertainty and multiple-valid-answer contracts;
- reference integrations for selected open evaluation frameworks.

## Non-goals

Declaring a source scientifically correct, replacing assurance, grading unrestricted prose, or presenting synthetic fixtures as climate facts remain out of scope.
