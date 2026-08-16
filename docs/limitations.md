# Limitations

- Bundled records are synthetic and must never be cited as current climate evidence.
- The unit registry is intentionally small; it does not handle compound intensity units, gases with GWP conversion, currencies, temperature offsets, uncertainty distributions, or methodological equivalence.
- Geography and entity checks use conservative normalized equality, not entity resolution.
- Citation checks validate source identifiers and dates, not document content, authorship, provenance chains, or claim entailment.
- A source validity interval is supplied by the benchmark author and is only as trustworthy as benchmark curation. Dates must use exact calendar-valid `YYYY-MM-DD` syntax, `valid_from` cannot follow `valid_until`, and `published_on` cannot follow `valid_until`.
- Numeric tolerance cannot assess whether a requested metric was conceptually appropriate.
- Expected values and tolerances must be representable as finite floating-point numbers; oversized JSON integers are rejected rather than coerced. Tolerances must be non-negative, relative tolerance must be at most `1.0`, and task/source identifiers must be unique within their scopes. Oversized answer values become `invalid_numeric` findings. Numeric acceptance uses only the declared tolerance; no absolute epsilon is added.
- Unit aliases are explicit. Whitespace and selected multiplication spellings such as `kW h` and `kW·h` are accepted, while division or other dimensional operators are never discarded (`kW/h` is not `kWh`).
- Equal-factor aliases preserve finite values exactly, including subnormals and the largest floats. Other conversions multiply once by the precomputed factor ratio; a mathematically non-representable result becomes an `invalid_numeric` finding while independent context and citation components are still evaluated.
- Empty task datasets and duplicate task or answer identifiers are validation errors; the evaluation CLI returns `2` and does not emit a report. Valid evaluations return `0` only when every task passes and `1` when any task fails; both valid outcomes emit reports.
- Report output path components and pre-existing artifacts must be real directories and regular files, not symbolic links. Reports and requested demo JSONL are staged before commit and restored as one prior set if publication fails partway through. Cooperating writers serialize publication with an advisory lock on the verified output directory; locking fails closed when unavailable, but cannot coordinate non-cooperating writers or filesystems that ignore `flock`-style locks.
- Component weights are a transparent demonstration policy, not an industry standard.
- The benchmark does not replace subject-matter review, source reading, or current authoritative data.
