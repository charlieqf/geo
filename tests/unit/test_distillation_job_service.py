import json
from pathlib import Path

from src.services.distillation_job_service import (
    build_initial_job_state,
    cancel_job,
    load_job_state,
    save_job_state,
)


def test_build_initial_job_state_creates_pending_question_progress() -> None:
    draft = {
        "draft_id": "draft-1",
        "keyword": "中国 GEO 服务",
        "brand": "流量玩家",
        "questions": [
            {
                "question_id": "Q001",
                "question_group": "generic",
                "intent_bucket": "direct_recommendation",
                "question": "中国 GEO 服务哪家值得优先了解？",
            }
        ],
    }

    state = build_initial_job_state(job_id="job-1", draft=draft)

    assert state["job_id"] == "job-1"
    assert state["status"] == "running"
    assert state["draft_id"] == "draft-1"
    assert state["progress_rows"]["Q001"]["status"] == "pending"


def test_save_and_load_job_state_round_trip(tmp_path: Path) -> None:
    state_path = tmp_path / "job.json"
    payload = {
        "job_id": "job-1",
        "status": "running",
        "progress_rows": {"Q001": {"status": "running"}},
    }

    save_job_state(state_path, payload)
    loaded = load_job_state(state_path)

    assert loaded == payload


def test_cancel_job_marks_running_job_as_cancelling(tmp_path: Path) -> None:
    state_path = tmp_path / "job.json"
    payload = {
        "job_id": "job-1",
        "status": "running",
        "cancel_requested": False,
        "progress_rows": {"Q001": {"status": "running"}},
    }
    save_job_state(state_path, payload)

    updated = cancel_job(state_path)

    assert updated is not None
    assert updated["status"] == "cancelling"
    assert updated["cancel_requested"] is True
    reloaded = load_job_state(state_path)
    assert reloaded is not None
    assert reloaded["status"] == "cancelling"


def test_cancel_job_keeps_completed_job_unchanged(tmp_path: Path) -> None:
    state_path = tmp_path / "job.json"
    payload = {
        "job_id": "job-1",
        "status": "completed",
        "cancel_requested": False,
        "progress_rows": {},
    }
    save_job_state(state_path, payload)

    updated = cancel_job(state_path)

    assert updated is not None
    assert updated["status"] == "completed"
    assert updated["cancel_requested"] is False
