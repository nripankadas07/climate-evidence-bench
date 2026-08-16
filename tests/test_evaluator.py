import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from climate_evidence_bench.demo import demo_records
from climate_evidence_bench.evaluator import evaluate_records, evaluate_task


class EvaluatorTests(unittest.TestCase):
    def test_demo_is_deterministic(self):
        tasks, answers = demo_records()
        self.assertEqual(evaluate_records(tasks, answers), evaluate_records(tasks, answers))

    def test_unit_conversion_task_passes(self):
        tasks, answers = demo_records()
        result = evaluate_task(tasks[0], answers[0])
        self.assertTrue(result["passed"])
        self.assertEqual(result["converted_value_in_expected_unit"], 2.4)

    def test_failure_taxonomy_is_specific(self):
        tasks, answers = demo_records()
        result = evaluate_records(tasks, answers)
        codes = {failure["code"] for item in result["tasks"] for failure in item["failures"]}
        self.assertIn("numeric_out_of_tolerance", codes)
        self.assertIn("unit_dimension_mismatch", codes)
        self.assertIn("year_mismatch", codes)
        self.assertIn("geography_mismatch", codes)
        self.assertIn("entity_mismatch", codes)
        self.assertIn("citation_source_mismatch", codes)
        self.assertIn("citation_stale", codes)

    def test_missing_answer(self):
        tasks, _ = demo_records()
        result = evaluate_task(tasks[0], None)
        self.assertEqual(result["failures"][0]["code"], "missing_answer")

    def test_invalid_answer_schema_cannot_pass(self):
        tasks, answers = demo_records()
        malformed = dict(answers[0])
        malformed["schema_version"] = "999.0.0"
        result = evaluate_task(tasks[0], malformed)
        self.assertFalse(result["passed"])
        self.assertIn("malformed_record", {item["code"] for item in result["failures"]})

    def test_dimensionally_wrong_operator_unit_cannot_pass(self):
        tasks, answers = demo_records()
        task = copy.deepcopy(tasks[0])
        answer = copy.deepcopy(answers[0])
        task["expected"].update(value=1.0, unit="kWh")
        task["tolerance"] = {"absolute": 0.0, "relative": 0.0}
        answer.update(value=1.0, unit="kW/h")
        result = evaluate_task(task, answer)
        self.assertFalse(result["passed"])
        self.assertFalse(result["components"]["unit"])
        self.assertIn("unsupported_unit", {item["code"] for item in result["failures"]})

    def test_non_finite_and_out_of_range_tolerances_are_rejected(self):
        tasks, answers = demo_records()
        bad_values = [
            {"absolute": json.loads("1e309"), "relative": 0.0},
            {"absolute": -1.0, "relative": 0.0},
            {"absolute": 0.0, "relative": 1.01},
        ]
        for tolerance in bad_values:
            with self.subTest(tolerance=tolerance):
                task = copy.deepcopy(tasks[0])
                task["tolerance"] = tolerance
                with self.assertRaises(ValueError):
                    evaluate_task(task, answers[0])

    def test_malformed_nested_citation_uses_stable_taxonomy(self):
        tasks, answers = demo_records()
        malformed = copy.deepcopy(answers[0])
        malformed["citations"] = [{"source_id": []}]
        result = evaluate_task(tasks[0], malformed)
        self.assertFalse(result["passed"])
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["failures"][0]["code"], "malformed_record")

    def test_empty_and_duplicate_datasets_are_rejected(self):
        tasks, answers = demo_records()
        with self.assertRaisesRegex(ValueError, "at least one task"):
            evaluate_records([], [])
        with self.assertRaisesRegex(ValueError, "duplicate task IDs"):
            evaluate_records([tasks[0], copy.deepcopy(tasks[0])], [answers[0]])
        with self.assertRaisesRegex(ValueError, "duplicate answer IDs"):
            evaluate_records([tasks[0]], [answers[0], copy.deepcopy(answers[0])])

    def test_nested_task_dates_are_validated(self):
        tasks, answers = demo_records()
        task = copy.deepcopy(tasks[0])
        task["accepted_sources"][0]["valid_from"] = "not-a-date"
        with self.assertRaisesRegex(ValueError, "must be an ISO date"):
            evaluate_task(task, answers[0])

    def test_zero_tolerance_has_no_hidden_absolute_epsilon(self):
        tasks, answers = demo_records()
        task = copy.deepcopy(tasks[0])
        answer = copy.deepcopy(answers[0])
        task["expected"]["value"] = 5e-13
        task["tolerance"] = {"absolute": 0.0, "relative": 0.0}
        answer["value"] = 0.0
        result = evaluate_task(task, answer)
        self.assertFalse(result["passed"])
        self.assertFalse(result["components"]["numeric"])
        self.assertIn(
            "numeric_out_of_tolerance",
            {failure["code"] for failure in result["failures"]},
        )

    def test_dates_require_exact_calendar_valid_yyyy_mm_dd(self):
        tasks, answers = demo_records()
        for candidate in ("20310630", "2031-W26-1", "2031-02-29"):
            with self.subTest(candidate=candidate):
                task = copy.deepcopy(tasks[0])
                task["evaluation_as_of"] = candidate
                with self.assertRaisesRegex(ValueError, "must be an ISO date"):
                    evaluate_task(task, answers[0])

    def test_source_publication_cannot_follow_validity_end(self):
        tasks, answers = demo_records()
        task = copy.deepcopy(tasks[0])
        source = task["accepted_sources"][0]
        source["published_on"] = "2031-07-01"
        source["valid_until"] = "2031-06-30"
        with self.assertRaisesRegex(ValueError, "published_on must not be after valid_until"):
            evaluate_task(task, answers[0])


if __name__ == "__main__":
    unittest.main()
