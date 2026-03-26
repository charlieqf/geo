from pathlib import Path


def test_distill_page_source_uses_latest_job_state_and_not_popover() -> None:
    content = Path("pages/3_运行蒸馏.py").read_text(encoding="utf-8")

    assert "latest_job_meta_for_draft" in content
    assert 'st.popover(DISTILL_PAGE["view_answers"])' not in content
    assert "distillation_preview_question_id" in content
