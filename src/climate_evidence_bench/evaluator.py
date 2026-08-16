"""Deterministic task evaluator and stable failure taxonomy."""

import math
import re
from collections import Counter
from datetime import date
from statistics import fmean
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import SCHEMA_VERSION, __version__
from .units import UnitDimensionMismatch, UnsupportedUnit, convert, describe


SYNTHETIC_NOTICE = (
    "Every bundled entity, geography, measurement, and source is synthetic "
    "benchmark data. No record is a current climate fact."
)

FAILURE_TAXONOMY = {
    "missing_answer": "No answer record was supplied for the task.",
    "malformed_record": "A task or answer is missing a required field or has an invalid type.",
    "invalid_numeric": "The answer value is absent, non-numeric, or non-finite.",
    "unsupported_unit": "The answer or expected unit is outside the explicit registry.",
    "unit_dimension_mismatch": "Answer and expected units describe different dimensions.",
    "numeric_out_of_tolerance": "The converted answer is outside absolute and relative tolerance.",
    "year_mismatch": "The answer year differs from the requested entity-year context.",
    "geography_mismatch": "The answer geography differs after conservative normalization.",
    "entity_mismatch": "The answer entity differs after conservative normalization.",
    "missing_citation": "The answer includes no citation.",
    "citation_source_mismatch": "No cited source is accepted for this task.",
    "citation_future_dated": "The selected source was published after the evaluation as-of date.",
    "citation_not_yet_valid": "The selected source was not yet valid on the as-of date.",
    "citation_stale": "The selected source had expired before the as-of date.",
}

COMPONENT_WEIGHTS = {
    "numeric": 0.30,
    "unit": 0.10,
    "year": 0.10,
    "geography": 0.10,
    "entity": 0.10,
    "citation": 0.20,
    "temporal_validity": 0.10,
}


def _normalized_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().casefold())


def _parse_date(value: str) -> date:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        raise ValueError("date must use exact YYYY-MM-DD syntax")
    return date.fromisoformat(value)


def _failure(code: str, message: Optional[str] = None) -> Dict[str, str]:
    return {"code": code, "message": message or FAILURE_TAXONOMY[code]}


def _validate_task(task: Dict[str, Any]) -> None:
    if not isinstance(task, dict):
        raise ValueError("task record must be an object")
    required = {
        "schema_version",
        "artifact_type",
        "task_id",
        "prompt",
        "expected",
        "tolerance",
        "evaluation_as_of",
        "accepted_sources",
    }
    missing = sorted(required - set(task))
    if missing:
        raise ValueError("task missing fields: {0}".format(", ".join(missing)))
    if task["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported task schema_version")
    if task["artifact_type"] != "climate-evidence-bench.task":
        raise ValueError("unexpected task artifact_type")
    if not isinstance(task["task_id"], str) or not task["task_id"].strip():
        raise ValueError("task_id must be a non-empty string")
    if not isinstance(task["prompt"], str) or not task["prompt"].strip():
        raise ValueError("task prompt must be a non-empty string")
    if not isinstance(task["expected"], dict):
        raise ValueError("task expected must be an object")
    for key in ("value", "unit", "year", "geography", "entity"):
        if key not in task["expected"]:
            raise ValueError("task expected missing {0}".format(key))
    expected = task["expected"]
    expected_value = expected["value"]
    if (
        isinstance(expected_value, bool)
        or not isinstance(expected_value, (int, float))
        or not math.isfinite(float(expected_value))
    ):
        raise ValueError("task expected.value must be a finite number")
    if not isinstance(expected["unit"], str) or not expected["unit"].strip():
        raise ValueError("task expected.unit must be a non-empty string")
    try:
        describe(expected["unit"])
    except UnsupportedUnit as exc:
        raise ValueError("task expected.unit is unsupported: {0}".format(expected["unit"])) from exc
    if isinstance(expected["year"], bool) or not isinstance(expected["year"], int):
        raise ValueError("task expected.year must be an integer")
    for field in ("geography", "entity"):
        if not isinstance(expected[field], str) or not expected[field].strip():
            raise ValueError("task expected.{0} must be a non-empty string".format(field))

    tolerance = task["tolerance"]
    if not isinstance(tolerance, dict):
        raise ValueError("task tolerance must be an object")
    for field in ("absolute", "relative"):
        if field not in tolerance:
            raise ValueError("task tolerance missing {0}".format(field))
        candidate = tolerance[field]
        if (
            isinstance(candidate, bool)
            or not isinstance(candidate, (int, float))
            or not math.isfinite(float(candidate))
            or candidate < 0
        ):
            raise ValueError("task tolerance.{0} must be a finite non-negative number".format(field))
    if tolerance["relative"] > 1:
        raise ValueError("task tolerance.relative must be between zero and one")

    if not isinstance(task["evaluation_as_of"], str):
        raise ValueError("task evaluation_as_of must be an ISO date")
    try:
        _parse_date(task["evaluation_as_of"])
    except (TypeError, ValueError) as exc:
        raise ValueError("task evaluation_as_of must be an ISO date") from exc

    sources = task["accepted_sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("task accepted_sources must not be empty")
    source_ids: List[str] = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError("task accepted_sources[{0}] must be an object".format(index))
        for field in ("source_id", "published_on", "valid_from", "valid_until"):
            if field not in source:
                raise ValueError("task accepted_sources[{0}] missing {1}".format(index, field))
        source_id = source["source_id"]
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("task accepted_sources[{0}].source_id must be a non-empty string".format(index))
        source_ids.append(source_id)
        dates: Dict[str, date] = {}
        for field in ("published_on", "valid_from", "valid_until"):
            if not isinstance(source[field], str):
                raise ValueError("task accepted_sources[{0}].{1} must be an ISO date".format(index, field))
            try:
                dates[field] = _parse_date(source[field])
            except (TypeError, ValueError) as exc:
                raise ValueError("task accepted_sources[{0}].{1} must be an ISO date".format(index, field)) from exc
        if dates["valid_from"] > dates["valid_until"]:
            raise ValueError("task accepted_sources[{0}] validity interval is inverted".format(index))
        if dates["published_on"] > dates["valid_until"]:
            raise ValueError(
                "task accepted_sources[{0}].published_on must not be after valid_until".format(
                    index
                )
            )
    duplicates = sorted(identifier for identifier, count in Counter(source_ids).items() if count > 1)
    if duplicates:
        raise ValueError("task accepted source IDs must be unique: {0}".format(", ".join(duplicates)))


def _answer_errors(answer: Any, task_id: str) -> List[str]:
    if not isinstance(answer, dict):
        return ["answer record must be an object"]
    errors: List[str] = []
    if answer.get("schema_version") != SCHEMA_VERSION:
        errors.append("answer has an unsupported schema_version")
    if answer.get("artifact_type") != "climate-evidence-bench.answer":
        errors.append("answer has an unexpected artifact_type")
    answer_task_id = answer.get("task_id")
    if not isinstance(answer_task_id, str) or not answer_task_id.strip():
        errors.append("answer task_id must be a non-empty string")
    elif answer_task_id != task_id:
        errors.append("answer task_id does not match the task")
    if isinstance(answer.get("year"), bool) or not isinstance(answer.get("year"), int):
        errors.append("answer year must be an integer")
    for field in ("geography", "entity"):
        if not isinstance(answer.get(field), str) or not answer.get(field, "").strip():
            errors.append("answer {0} must be a non-empty string".format(field))
    citations = answer.get("citations")
    if citations is not None:
        if not isinstance(citations, list):
            errors.append("answer citations must be an array")
        else:
            for index, citation in enumerate(citations):
                if not isinstance(citation, dict):
                    errors.append("answer citations[{0}] must be an object".format(index))
                elif not isinstance(citation.get("source_id"), str) or not citation.get("source_id", "").strip():
                    errors.append("answer citations[{0}].source_id must be a non-empty string".format(index))
    return errors


def evaluate_task(task: Dict[str, Any], answer: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    _validate_task(task)
    expected = task["expected"]
    components = {name: False for name in COMPONENT_WEIGHTS}
    failures: List[Dict[str, str]] = []
    converted_value: Optional[float] = None

    if answer is None:
        failures.append(_failure("missing_answer"))
        return _task_result(task, components, failures, converted_value)

    answer_errors = _answer_errors(answer, task["task_id"])
    if answer_errors:
        failures.append(_failure("malformed_record", "; ".join(answer_errors)))
        return _task_result(task, components, failures, converted_value)

    # Unit and numeric evaluation.
    answer_value = answer.get("value")
    answer_unit = answer.get("unit")
    if not isinstance(answer_value, (int, float)) or isinstance(answer_value, bool) or not math.isfinite(float(answer_value)):
        failures.append(_failure("invalid_numeric"))
    elif not isinstance(answer_unit, str):
        failures.append(_failure("unsupported_unit", "Answer unit is missing or not a string."))
    else:
        try:
            describe(str(expected["unit"]))
            describe(answer_unit)
            candidate_value = convert(float(answer_value), answer_unit, str(expected["unit"]))
            components["unit"] = True
            if not math.isfinite(candidate_value):
                failures.append(_failure("invalid_numeric", "Converted answer value is non-finite."))
                return _task_result(task, components, failures, converted_value)
            converted_value = candidate_value
            difference = abs(converted_value - float(expected["value"]))
            tolerance = task["tolerance"]
            allowed = max(
                float(tolerance["absolute"]),
                abs(float(expected["value"])) * float(tolerance["relative"]),
            )
            if difference <= allowed:
                components["numeric"] = True
            else:
                failures.append(
                    _failure(
                        "numeric_out_of_tolerance",
                        "Converted value {0:.9g} differs from {1:.9g}; allowed {2:.9g}.".format(
                            converted_value, float(expected["value"]), allowed
                        ),
                    )
                )
        except UnsupportedUnit as exc:
            failures.append(_failure("unsupported_unit", str(exc)))
        except UnitDimensionMismatch as exc:
            failures.append(_failure("unit_dimension_mismatch", str(exc)))

    # Entity context.
    if answer.get("year") == expected["year"]:
        components["year"] = True
    else:
        failures.append(_failure("year_mismatch"))
    if _normalized_text(answer.get("geography", "")) == _normalized_text(expected["geography"]):
        components["geography"] = True
    else:
        failures.append(_failure("geography_mismatch"))
    if _normalized_text(answer.get("entity", "")) == _normalized_text(expected["entity"]):
        components["entity"] = True
    else:
        failures.append(_failure("entity_mismatch"))

    # Citation and temporal validity.
    citations = answer.get("citations")
    if not isinstance(citations, list) or not citations:
        failures.append(_failure("missing_citation"))
    else:
        accepted = {source["source_id"]: source for source in task["accepted_sources"]}
        selected: List[Dict[str, Any]] = []
        for citation in citations:
            if isinstance(citation, dict) and citation.get("source_id") in accepted:
                selected.append(accepted[citation["source_id"]])
        if selected:
            components["citation"] = True
            as_of = _parse_date(task["evaluation_as_of"])
            temporal_pass = False
            temporal_failures: List[Dict[str, str]] = []
            for source in selected:
                published = _parse_date(source["published_on"])
                valid_from = _parse_date(source["valid_from"])
                valid_until = _parse_date(source["valid_until"])
                if published > as_of:
                    temporal_failures.append(_failure("citation_future_dated"))
                elif valid_from > as_of:
                    temporal_failures.append(_failure("citation_not_yet_valid"))
                elif valid_until < as_of:
                    temporal_failures.append(_failure("citation_stale"))
                else:
                    temporal_pass = True
                    break
            if temporal_pass:
                components["temporal_validity"] = True
            else:
                failures.extend(temporal_failures[:1])
        else:
            failures.append(_failure("citation_source_mismatch"))

    return _task_result(task, components, failures, converted_value)


def _task_result(
    task: Dict[str, Any],
    components: Dict[str, bool],
    failures: List[Dict[str, str]],
    converted_value: Optional[float],
) -> Dict[str, Any]:
    score = sum(COMPONENT_WEIGHTS[name] for name, passed in components.items() if passed)
    return {
        "task_id": task["task_id"],
        "score": round(score, 6),
        "passed": all(components.values()) and not failures,
        "components": components,
        "converted_value_in_expected_unit": (
            round(converted_value, 9) if converted_value is not None else None
        ),
        "failures": failures,
    }


def evaluate_records(
    tasks: Iterable[Dict[str, Any]], answers: Iterable[Dict[str, Any]]
) -> Dict[str, Any]:
    task_list = list(tasks)
    if not task_list:
        raise ValueError("task dataset must contain at least one task")
    for task in task_list:
        _validate_task(task)
    task_ids = [task["task_id"] for task in task_list]
    duplicate_task_ids = sorted(
        identifier for identifier, count in Counter(task_ids).items() if count > 1
    )
    if duplicate_task_ids:
        raise ValueError("duplicate task IDs: {0}".format(", ".join(duplicate_task_ids)))

    answer_list = list(answers)
    answer_map: Dict[str, Dict[str, Any]] = {}
    answer_ids: List[str] = []
    for index, answer in enumerate(answer_list):
        if not isinstance(answer, dict):
            raise ValueError("answer record {0} must be an object".format(index))
        task_id = answer.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("answer record {0} requires a non-empty task_id".format(index))
        answer_ids.append(task_id)
        answer_map[task_id] = answer
    duplicate_answer_ids = sorted(
        identifier for identifier, count in Counter(answer_ids).items() if count > 1
    )
    if duplicate_answer_ids:
        raise ValueError("duplicate answer IDs: {0}".format(", ".join(duplicate_answer_ids)))
    results = [evaluate_task(task, answer_map.get(task["task_id"])) for task in task_list]
    component_rates = {
        name: (
            sum(result["components"][name] for result in results) / len(results)
            if results
            else 0.0
        )
        for name in COMPONENT_WEIGHTS
    }
    failure_counts = Counter(
        failure["code"] for result in results for failure in result["failures"]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "climate-evidence-bench.evaluation-report",
        "generator": {"name": "climate-evidence-bench", "version": __version__},
        "synthetic_notice": SYNTHETIC_NOTICE,
        "metrics": {
            "task_count": len(results),
            "passed_count": sum(result["passed"] for result in results),
            "pass_rate": round(
                sum(result["passed"] for result in results) / len(results) if results else 0.0,
                6,
            ),
            "mean_score": round(fmean(result["score"] for result in results), 6) if results else 0.0,
            "component_pass_rates": {
                name: round(value, 6) for name, value in component_rates.items()
            },
            "failure_counts": dict(sorted(failure_counts.items())),
            "duplicate_answer_ids": [],
            "orphan_answer_ids": sorted(set(answer_map) - set(task_ids)),
        },
        "failure_taxonomy": FAILURE_TAXONOMY,
        "component_weights": COMPONENT_WEIGHTS,
        "tasks": results,
    }
