"""JSONL adapters for task and answer records."""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError("invalid JSONL at {0}:{1}: {2}".format(path, line_number, exc)) from exc
        if not isinstance(value, dict):
            raise ValueError("JSONL record at {0}:{1} must be an object".format(path, line_number))
        records.append(value)
    return records


def write_jsonl(records: Iterable[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(
        json.dumps(record, sort_keys=True, allow_nan=False) + "\n" for record in records
    )
    path.write_text(text, encoding="utf-8")
