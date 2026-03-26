from pathlib import Path


def test_results_trace_page_shows_variant_explanations() -> None:
    content = Path("pages/4_结果分析.py").read_text(encoding="utf-8")

    assert "PROMPT_VARIANT_EXPLANATIONS" in content
    assert "trace_variant_explanation" in content
