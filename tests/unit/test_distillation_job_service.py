import json
from pathlib import Path

from src.services.distillation_job_service import latest_job_meta_for_draft


def _write_job(path: Path, *, draft_id: str, updated_at: str) -> None:
    path.write_text(
        json.dumps(
            {
                "job_id": path.stem,
                "draft_id": draft_id,
                "updated_at": updated_at,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_latest_job_meta_for_draft_returns_most_recent_matching_job(
    tmp_path: Path,
) -> None:
    jobs_dir = tmp_path / "jobs"
    jobs_dir.mkdir(parents=True)
    _write_job(
        jobs_dir / "job-older.json",
        draft_id="draft-a",
        updated_at="2026-03-25T02:00:00+00:00",
    )
    _write_job(
        jobs_dir / "job-newer.json",
        draft_id="draft-a",
        updated_at="2026-03-25T03:00:00+00:00",
    )

    result = latest_job_meta_for_draft(tmp_path, "draft-a")

    assert result is not None
    assert result["job_id"] == "job-newer"
    assert result["state_path"].endswith("job-newer.json")
    assert result["log_path"].endswith("job-newer.log")


def test_latest_job_meta_for_draft_ignores_other_drafts(tmp_path: Path) -> None:
    jobs_dir = tmp_path / "jobs"
    jobs_dir.mkdir(parents=True)
    _write_job(
        jobs_dir / "job-a.json",
        draft_id="draft-a",
        updated_at="2026-03-25T02:00:00+00:00",
    )
    _write_job(
        jobs_dir / "job-b.json",
        draft_id="draft-b",
        updated_at="2026-03-25T03:00:00+00:00",
    )

    result = latest_job_meta_for_draft(tmp_path, "draft-a")

    assert result is not None
    assert result["job_id"] == "job-a"
