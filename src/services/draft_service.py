from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def list_question_drafts(drafts_dir: Path) -> list[dict[str, Any]]:
    if not drafts_dir.exists():
        return []
    drafts: list[dict[str, Any]] = []
    for draft_path in sorted(
        drafts_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True
    ):
        payload = json.loads(draft_path.read_text(encoding="utf-8"))
        payload["draft_path"] = str(draft_path)
        drafts.append(payload)
    return drafts


def load_question_draft(draft_path: Path) -> dict[str, Any]:
    payload = json.loads(draft_path.read_text(encoding="utf-8"))
    payload["draft_path"] = str(draft_path)
    return payload


def format_draft_label(draft_id: str) -> str:
    cleaned = draft_id.replace("draft-", "")
    return f"问题池 · {cleaned}"
