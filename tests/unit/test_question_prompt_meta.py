from pathlib import Path

from src.services.prompt_meta_service import load_prompt_meta


def test_load_prompt_meta_reads_question_pool_metadata() -> None:
    payload = load_prompt_meta(Path("prompts") / "question_pool_prompt.json")

    assert payload["title"] == "问题池生成 Prompt"
    assert payload["default_question_count"] == 15
    assert payload["brand_question_count"] == 6
    assert "brand_instruction" in payload["variables"]
