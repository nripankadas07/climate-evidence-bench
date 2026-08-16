"""Explicitly synthetic benchmark fixtures."""

from typing import Any, Dict, List, Tuple

from . import SCHEMA_VERSION


NOTICE = "Synthetic benchmark record; not a current climate fact."


def _source(source_id: str, published: str, start: str, end: str) -> Dict[str, str]:
    return {
        "source_id": source_id,
        "uri": "synthetic://climate-evidence-bench/{0}".format(source_id),
        "published_on": published,
        "valid_from": start,
        "valid_until": end,
        "synthetic_notice": NOTICE,
    }


def _task(
    task_id: str,
    prompt: str,
    value: float,
    unit: str,
    year: int,
    geography: str,
    entity: str,
    sources: List[Dict[str, str]],
    as_of: str,
    absolute: float,
    relative: float = 0.01,
) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "climate-evidence-bench.task",
        "task_id": task_id,
        "prompt": prompt + " " + NOTICE,
        "expected": {
            "value": value,
            "unit": unit,
            "year": year,
            "geography": geography,
            "entity": entity,
        },
        "tolerance": {"absolute": absolute, "relative": relative},
        "evaluation_as_of": as_of,
        "accepted_sources": sources,
        "synthetic_notice": NOTICE,
    }


def _answer(task_id: str, value: float, unit: str, year: int, geography: str, entity: str, source_id: str) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "climate-evidence-bench.answer",
        "task_id": task_id,
        "value": value,
        "unit": unit,
        "year": year,
        "geography": geography,
        "entity": entity,
        "citations": [{"source_id": source_id}],
        "synthetic_notice": NOTICE,
    }


def demo_records() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    current_a = _source("SYN-SRC-A", "2029-03-01", "2029-01-01", "2034-12-31")
    current_b = _source("SYN-SRC-B", "2030-02-10", "2030-01-01", "2035-12-31")
    old_c = _source("SYN-SRC-C-OLD", "2025-01-15", "2025-01-01", "2027-12-31")
    current_c = _source("SYN-SRC-C", "2028-01-15", "2028-01-01", "2033-12-31")
    tasks = [
        _task("unit-conversion-pass", "Report synthetic emissions for Demo Utility A.", 2.4, "MtCO2e", 2031, "Synthetic Delta", "Demo Utility A", [current_a], "2031-06-30", 0.01),
        _task("tolerance-fail", "Report synthetic renewable output.", 850.0, "GWh", 2032, "Synthetic Coast", "Demo Grid B", [current_b], "2032-08-01", 2.0, 0.002),
        _task("dimension-fail", "Report synthetic avoided emissions.", 420.0, "ktCO2e", 2030, "Synthetic Basin", "Demo Program C", [current_b], "2030-09-01", 1.0),
        _task("context-fail", "Report the synthetic intensity indicator.", 0.42, "fraction", 2033, "Synthetic North", "Demo Facility D", [current_a], "2033-05-01", 0.005),
        _task("source-fail", "Report synthetic land coverage.", 1250.0, "ha", 2030, "Synthetic Plain", "Demo Project E", [current_b], "2030-07-01", 5.0),
        _task("temporal-fail", "Report synthetic water volume.", 4000.0, "m3", 2030, "Synthetic Valley", "Demo Site F", [old_c, current_c], "2030-06-01", 10.0),
    ]
    answers = [
        _answer("unit-conversion-pass", 2400.0, "ktCO2e", 2031, " synthetic   delta ", "Demo Utility A", "SYN-SRC-A"),
        _answer("tolerance-fail", 900.0, "GWh", 2032, "Synthetic Coast", "Demo Grid B", "SYN-SRC-B"),
        _answer("dimension-fail", 420.0, "GWh", 2030, "Synthetic Basin", "Demo Program C", "SYN-SRC-B"),
        _answer("context-fail", 42.0, "%", 2032, "Synthetic South", "Demo Facility X", "SYN-SRC-A"),
        _answer("source-fail", 12.5, "km2", 2030, "Synthetic Plain", "Demo Project E", "SYN-UNACCEPTED"),
        _answer("temporal-fail", 4_000_000.0, "L", 2030, "Synthetic Valley", "Demo Site F", "SYN-SRC-C-OLD"),
    ]
    return tasks, answers
