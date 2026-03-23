import json
from pathlib import Path

from src.services.run_service import (
    list_runs,
    load_prompt_content,
    load_run_artifacts,
    save_prompt_content,
)


def test_list_runs_reads_summary_files(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "discovery-1"
    run_dir.mkdir(parents=True)
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "variants": {"web_ranked_analysis": {"answer_count": 4}},
                "top_actionable_platforms": [["知乎", 6], ["小红书", 5]],
                "benchmark_summary": {"web_ranked_analysis": 0.9},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    runs = list_runs(tmp_path / "runs")

    assert len(runs) == 1
    assert runs[0]["run_id"] == "discovery-1"
    assert runs[0]["top_actionable_platforms"] == [["知乎", 6], ["小红书", 5]]
    assert runs[0]["benchmark_summary"] == {"web_ranked_analysis": 0.9}


def test_load_and_save_prompt_content_round_trip(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir(parents=True)
    prompt_path = prompts_dir / "qwen_web_default.md"
    prompt_path.write_text("old content", encoding="utf-8")

    assert load_prompt_content(prompt_path) == "old content"

    save_prompt_content(prompt_path, "new content")

    assert load_prompt_content(prompt_path) == "new content"


def test_load_run_artifacts_reads_questions_and_answers(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "discovery-2"
    run_dir.mkdir(parents=True)
    (run_dir / "questions.json").write_text(
        json.dumps([{"question_id": "q1", "question": "test"}], ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "answers.json").write_text(
        json.dumps([{"question_id": "q1", "text": "answer"}], ensure_ascii=False),
        encoding="utf-8",
    )

    artifacts = load_run_artifacts(run_dir)

    assert artifacts["questions"] == [{"question_id": "q1", "question": "test"}]
    assert artifacts["answers"] == [{"question_id": "q1", "text": "answer"}]
