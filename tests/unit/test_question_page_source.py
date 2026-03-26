from pathlib import Path


def test_question_page_source_wires_draft_selector() -> None:
    content = Path("pages/2_蒸馏问题生成.py").read_text(encoding="utf-8")

    assert 'QUESTION_PAGE["draft_selector"]' in content
    assert "st.selectbox(" in content
