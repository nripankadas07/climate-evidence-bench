"""JSON, Markdown, and single-file HTML evaluation reports."""

import html
import json
import re
from pathlib import Path
from typing import Any, Dict


def _markdown_text(value: Any) -> str:
    """Render untrusted values as one inert Markdown line."""
    text = re.sub(r"\s+", " ", str(value)).strip()
    text = html.escape(text, quote=False)
    return text.replace("`", "&#96;").replace("|", "&#124;")


def _markdown(result: Dict[str, Any]) -> str:
    metrics = result["metrics"]
    lines = [
        "# Climate Evidence Bench report",
        "",
        "> **Synthetic benchmark:** {0}".format(_markdown_text(result["synthetic_notice"])),
        "",
        "- Schema: `{0}`".format(result["schema_version"]),
        "- Tasks: `{0}`".format(metrics["task_count"]),
        "- Fully passed: `{0}`".format(metrics["passed_count"]),
        "- Pass rate: `{0:.2%}`".format(metrics["pass_rate"]),
        "- Mean weighted score: `{0:.3f}`".format(metrics["mean_score"]),
        "",
        "## Component pass rates",
        "",
        "| Component | Pass rate |",
        "|---|---:|",
    ]
    for name, value in metrics["component_pass_rates"].items():
        lines.append("| {0} | {1:.2%} |".format(name.replace("_", " ").title(), value))
    lines.extend(["", "## Task results", "", "| Task | Score | Pass | Failures |", "|---|---:|:---:|---|"])
    for task in result["tasks"]:
        failures = ", ".join(item["code"] for item in task["failures"]) or "—"
        lines.append(
            "| `{0}` | {1:.2f} | {2} | {3} |".format(
                _markdown_text(task["task_id"]),
                task["score"],
                "yes" if task["passed"] else "no",
                _markdown_text(failures),
            )
        )
    lines.extend(["", "## Failure taxonomy", ""])
    for code, description in result["failure_taxonomy"].items():
        lines.append(
            "- `{0}` — {1}".format(_markdown_text(code), _markdown_text(description))
        )
    lines.extend(["", "All examples are synthetic and must not be cited as current climate facts.", ""])
    return "\n".join(lines)


def _html(result: Dict[str, Any]) -> str:
    metrics = result["metrics"]
    task_rows = "".join(
        "<tr><td>{0}</td><td>{1:.2f}</td><td>{2}</td><td>{3}</td></tr>".format(
            html.escape(task["task_id"]),
            task["score"],
            "PASS" if task["passed"] else "FAIL",
            html.escape(", ".join(item["code"] for item in task["failures"]) or "—"),
        )
        for task in result["tasks"]
    )
    component_rows = "".join(
        "<tr><td>{0}</td><td>{1:.1%}</td></tr>".format(html.escape(name), value)
        for name, value in metrics["component_pass_rates"].items()
    )
    embedded = html.escape(json.dumps(result, sort_keys=True, allow_nan=False))
    return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Climate Evidence Bench</title>
<style>body{{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:0 1rem;color:#17231f}}.notice{{background:#fff3cd;border-left:4px solid #d49a00;padding:1rem}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1rem;margin:1.5rem 0}}.card{{border:1px solid #d3ddd8;border-radius:10px;padding:1rem}}.value{{font-size:1.5rem;font-weight:700}}.tables{{display:grid;grid-template-columns:1fr 2fr;gap:2rem}}table{{border-collapse:collapse;width:100%}}th,td{{padding:.5rem;border-bottom:1px solid #dce4e0;text-align:left}}code{{word-break:break-all}}@media(max-width:750px){{.tables{{grid-template-columns:1fr}}}}</style>
<body><h1>Climate Evidence Bench</h1><p class="notice"><strong>Synthetic benchmark.</strong> {notice}</p><div class="cards"><div class="card"><div>Tasks</div><div class="value">{tasks}</div></div><div class="card"><div>Pass rate</div><div class="value">{pass_rate:.1%}</div></div><div class="card"><div>Mean score</div><div class="value">{mean_score:.3f}</div></div></div>
<div class="tables"><section><h2>Components</h2><table>{components}</table></section><section><h2>Tasks</h2><table><thead><tr><th>Task</th><th>Score</th><th>Status</th><th>Failures</th></tr></thead><tbody>{task_rows}</tbody></table></section></div>
<details><summary>Embedded versioned JSON artifact</summary><code>{embedded}</code></details></body></html>""".format(
        notice=html.escape(result["synthetic_notice"]),
        tasks=metrics["task_count"],
        pass_rate=metrics["pass_rate"],
        mean_score=metrics["mean_score"],
        components=component_rows,
        task_rows=task_rows,
        embedded=embedded,
    )


def write_reports(result: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_dir / "climate_evidence_report.json",
        "markdown": output_dir / "climate_evidence_report.md",
        "html": output_dir / "climate_evidence_report.html",
    }
    paths["json"].write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    paths["markdown"].write_text(_markdown(result), encoding="utf-8")
    paths["html"].write_text(_html(result), encoding="utf-8")
    return paths
