from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.pipeline.discovery_run import DistillationCancelledError, run_discovery
from src.services.distillation_job_service import load_job_state, save_job_state
from src.utils.time_utils import utc_now_iso


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a background distillation job.")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--draft-path", required=True)
    parser.add_argument("--state-path", required=True)
    parser.add_argument("--benchmark-path")
    args = parser.parse_args()

    config = load_config()
    draft_path = Path(args.draft_path)
    state_path = Path(args.state_path)
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    benchmark_text = None
    if args.benchmark_path:
        benchmark_file = Path(args.benchmark_path)
        if benchmark_file.exists():
            benchmark_text = benchmark_file.read_text(encoding="utf-8")

    state = load_job_state(state_path) or {}

    def on_progress(update: dict[str, object]) -> None:
        current_state = load_job_state(state_path) or state
        progress_rows = current_state.get("progress_rows", {})
        if isinstance(progress_rows, dict):
            progress_rows[str(update["question_id"])] = update
        current_state["progress_rows"] = progress_rows
        current_state["updated_at"] = utc_now_iso()
        save_job_state(state_path, current_state)

    def should_cancel() -> bool:
        current_state = load_job_state(state_path) or state
        return bool(current_state.get("cancel_requested"))

    try:
        result = run_discovery(
            config=config,
            keyword=draft["keyword"],
            questions=draft["questions"],
            benchmark_text=benchmark_text,
            progress_callback=on_progress,
            should_cancel=should_cancel,
        )
        final_state = load_job_state(state_path) or state
        final_state["status"] = "completed"
        final_state["run_id"] = result["run_id"]
        final_state["run_dir"] = result["run_dir"]
        final_state["updated_at"] = utc_now_iso()
        save_job_state(state_path, final_state)
    except DistillationCancelledError as exc:  # pragma: no cover - runtime path
        cancelled_state = load_job_state(state_path) or state
        progress_rows = cancelled_state.get("progress_rows", {})
        if isinstance(progress_rows, dict):
            for row in progress_rows.values():
                if isinstance(row, dict) and row.get("status") == "running":
                    row["status"] = "cancelled"
            cancelled_state["progress_rows"] = progress_rows
        cancelled_state["status"] = "cancelled"
        cancelled_state["error"] = str(exc)
        cancelled_state["updated_at"] = utc_now_iso()
        save_job_state(state_path, cancelled_state)
    except Exception as exc:  # pragma: no cover - runtime path
        error_state = load_job_state(state_path) or state
        error_state["status"] = "error"
        error_state["error"] = str(exc)
        error_state["updated_at"] = utc_now_iso()
        save_job_state(state_path, error_state)
        raise


if __name__ == "__main__":
    main()
