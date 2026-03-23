from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def list_runs(runs_dir: Path) -> list[dict[str, Any]]:
    if not runs_dir.exists():
        return []

    runs: list[dict[str, Any]] = []
    for summary_path in sorted(
        runs_dir.glob("*/summary.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    ):
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        runs.append(
            {
                "run_id": summary_path.parent.name,
                "summary_path": str(summary_path),
                "variants": payload.get("variants", {}),
                "top_actionable_platforms": payload.get("top_actionable_platforms", []),
                "top_domains": payload.get("top_domains", []),
                "benchmark_summary": payload.get("benchmark_summary", {}),
            }
        )
    return runs


def load_prompt_content(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8")


def save_prompt_content(prompt_path: Path, content: str) -> None:
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(content, encoding="utf-8")


def load_run_artifacts(run_dir: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for name in ("questions", "answers", "summary"):
        path = run_dir / f"{name}.json"
        payload[name] = (
            json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        )
    return payload


def format_run_label(run_id: str) -> str:
    cleaned = run_id.replace("discovery-", "")
    return f"实验 · {cleaned}"
