from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.ui_presenters import build_initial_question_progress
from src.utils.time_utils import utc_now_iso


def distillation_jobs_dir(runs_dir: Path) -> Path:
    return runs_dir / "jobs"


def job_state_path(runs_dir: Path, job_id: str) -> Path:
    return distillation_jobs_dir(runs_dir) / f"{job_id}.json"


def build_initial_job_state(*, job_id: str, draft: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "status": "running",
        "cancel_requested": False,
        "draft_id": draft["draft_id"],
        "keyword": draft["keyword"],
        "brand": draft.get("brand", ""),
        "run_id": None,
        "run_dir": None,
        "error": None,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "progress_rows": build_initial_question_progress(draft.get("questions", [])),
    }


def save_job_state(state_path: Path, payload: dict[str, Any]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_job_state(state_path: Path) -> dict[str, Any] | None:
    if not state_path.exists():
        return None
    return json.loads(state_path.read_text(encoding="utf-8"))


def cancel_job(state_path: Path) -> dict[str, Any] | None:
    state = load_job_state(state_path)
    if not state:
        return None
    if state.get("status") in {"completed", "error", "cancelled"}:
        return state
    state["cancel_requested"] = True
    state["status"] = "cancelling"
    state["updated_at"] = utc_now_iso()
    save_job_state(state_path, state)
    return state


def read_job_log_tail(log_path: Path, max_lines: int = 80) -> str:
    if not log_path.exists():
        return ""
    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(lines[-max_lines:])


def start_distillation_job(
    *,
    project_root: Path,
    runs_dir: Path,
    draft_path: Path,
    benchmark_path: Path | None,
) -> dict[str, Any]:
    job_id = f"job-{uuid4()}"
    state_path = job_state_path(runs_dir, job_id)
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    save_job_state(state_path, build_initial_job_state(job_id=job_id, draft=draft))

    command = [
        sys.executable,
        str(project_root / "scripts" / "run_distillation_job.py"),
        "--job-id",
        job_id,
        "--draft-path",
        str(draft_path),
        "--state-path",
        str(state_path),
    ]
    if benchmark_path is not None:
        command.extend(["--benchmark-path", str(benchmark_path)])

    log_path = distillation_jobs_dir(runs_dir) / f"{job_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = open(log_path, "ab")
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    subprocess.Popen(
        command,
        cwd=project_root,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    )
    return {
        "job_id": job_id,
        "state_path": str(state_path),
        "log_path": str(log_path),
    }
