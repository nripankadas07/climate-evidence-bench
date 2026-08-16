"""Command-line interface for Climate Evidence Bench."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .demo import demo_records
from .evaluator import evaluate_records
from .io import read_jsonl, write_jsonl
from .reporting import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="climate-evidence-bench", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="run the deterministic synthetic benchmark")
    demo.add_argument("--output-dir", type=Path, default=Path("reports"))
    demo.add_argument("--emit-jsonl", action="store_true", help="also emit task and answer JSONL")
    evaluate = sub.add_parser("evaluate", help="evaluate adapter-produced answer JSONL")
    evaluate.add_argument("--tasks", type=Path, required=True)
    evaluate.add_argument("--answers", type=Path, required=True)
    evaluate.add_argument("--output-dir", type=Path, default=Path("reports"))
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "demo":
            tasks, answers = demo_records()
            if args.emit_jsonl:
                write_jsonl(tasks, args.output_dir / "tasks.synthetic.jsonl")
                write_jsonl(answers, args.output_dir / "answers.synthetic.jsonl")
        else:
            tasks = read_jsonl(args.tasks)
            answers = read_jsonl(args.answers)
        result = evaluate_records(tasks, answers)
        paths = write_reports(result, args.output_dir)
        print("Synthetic benchmark data only; not current climate facts.")
        print("Pass rate: {0:.2%}; mean score: {1:.3f}".format(result["metrics"]["pass_rate"], result["metrics"]["mean_score"]))
        for kind, path in paths.items():
            print("{0}: {1}".format(kind, path.resolve()))
        if (
            args.command == "evaluate"
            and result["metrics"]["passed_count"] != result["metrics"]["task_count"]
        ):
            return 1
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print("climate-evidence-bench: error: {0}".format(exc), file=sys.stderr)
        return 2
