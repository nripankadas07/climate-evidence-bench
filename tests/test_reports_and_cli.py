import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from climate_evidence_bench.demo import demo_records
from climate_evidence_bench.evaluator import evaluate_records
from climate_evidence_bench.io import read_jsonl, write_jsonl
from climate_evidence_bench.reporting import write_reports


class ReportCliTests(unittest.TestCase):
    def test_jsonl_adapter_round_trip(self):
        tasks, _ = demo_records()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.jsonl"
            write_jsonl(tasks, path)
            self.assertEqual(read_jsonl(path), tasks)

    def test_checked_in_jsonl_has_one_json_value_per_line(self):
        for name in ("tasks.synthetic.jsonl", "answers.synthetic.jsonl"):
            with self.subTest(name=name):
                source = (ROOT / "examples" / name).read_text(encoding="utf-8")
                self.assertTrue(source.endswith("\n"))
                self.assertNotIn("\n\n", source)
                for line in source.splitlines():
                    self.assertIsInstance(json.loads(line), dict)

    def test_report_formats(self):
        result = evaluate_records(*demo_records())
        with tempfile.TemporaryDirectory() as directory:
            paths = write_reports(result, Path(directory))
            self.assertTrue(all(path.exists() for path in paths.values()))
            self.assertEqual(json.loads(paths["json"].read_text())["schema_version"], "1.0.0")
            self.assertIn("Synthetic benchmark", paths["html"].read_text())

    def test_cli_demo(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            completed = subprocess.run(
                [sys.executable, "-m", "climate_evidence_bench", "demo", "--emit-jsonl", "--output-dir", directory],
                cwd=str(ROOT), env=env, text=True, capture_output=True, check=False
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((Path(directory) / "climate_evidence_report.html").exists())
            self.assertTrue((Path(directory) / "tasks.synthetic.jsonl").exists())

    def test_golden_demo_matches(self):
        tasks, answers = demo_records()
        result = evaluate_records(tasks, answers)
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            paths = write_reports(result, directory_path)
            write_jsonl(tasks, directory_path / "tasks.synthetic.jsonl")
            write_jsonl(answers, directory_path / "answers.synthetic.jsonl")
            golden = ROOT / "artifacts" / "demo"
            for path in list(paths.values()) + [
                directory_path / "tasks.synthetic.jsonl",
                directory_path / "answers.synthetic.jsonl",
            ]:
                self.assertEqual(path.read_bytes(), (golden / path.name).read_bytes())

    def test_cli_rejects_empty_and_duplicate_datasets(self):
        tasks, answers = demo_records()
        cases = {
            "empty": ([], []),
            "duplicate-tasks": ([tasks[0], dict(tasks[0])], [answers[0]]),
            "duplicate-answers": ([tasks[0]], [answers[0], dict(answers[0])]),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            for name, (task_records, answer_records) in cases.items():
                with self.subTest(name=name):
                    task_path = root / (name + "-tasks.jsonl")
                    answer_path = root / (name + "-answers.jsonl")
                    write_jsonl(task_records, task_path)
                    write_jsonl(answer_records, answer_path)
                    completed = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "climate_evidence_bench",
                            "evaluate",
                            "--tasks",
                            str(task_path),
                            "--answers",
                            str(answer_path),
                            "--output-dir",
                            str(root / (name + "-out")),
                        ],
                        cwd=str(ROOT),
                        env=env,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(completed.returncode, 2)
                    self.assertIn("climate-evidence-bench: error:", completed.stderr)
                    self.assertNotIn("Traceback", completed.stderr)

    def test_markdown_neutralizes_untrusted_task_id(self):
        tasks, answers = demo_records()
        tasks = [dict(tasks[0])]
        answers = [dict(answers[0])]
        tasks[0]["task_id"] = "safe`\n\n## FORGED PASS RATE"
        answers[0]["task_id"] = tasks[0]["task_id"]
        result = evaluate_records(tasks, answers)
        with tempfile.TemporaryDirectory() as directory:
            markdown = write_reports(result, Path(directory))["markdown"].read_text(
                encoding="utf-8"
            )
        self.assertNotIn("\n## FORGED PASS RATE", markdown)
        self.assertIn("&#96;", markdown)

    def test_evaluate_cli_exit_status_distinguishes_findings_from_invalid_input(self):
        tasks, answers = demo_records()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            task_path = root / "tasks.jsonl"
            answer_path = root / "answers.jsonl"
            write_jsonl([tasks[0]], task_path)
            write_jsonl([answers[0]], answer_path)

            command = [
                sys.executable,
                "-m",
                "climate_evidence_bench",
                "evaluate",
                "--tasks",
                str(task_path),
                "--answers",
                str(answer_path),
                "--output-dir",
                str(root / "pass"),
            ]
            passed = subprocess.run(
                command,
                cwd=str(ROOT),
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertTrue((root / "pass" / "climate_evidence_report.json").exists())

            failing_answer = dict(answers[0])
            failing_answer["year"] = failing_answer["year"] + 1
            write_jsonl([failing_answer], answer_path)
            command[-1] = str(root / "fail")
            failed = subprocess.run(
                command,
                cwd=str(ROOT),
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(failed.returncode, 1, failed.stderr)
            self.assertTrue((root / "fail" / "climate_evidence_report.json").exists())


if __name__ == "__main__":
    unittest.main()
