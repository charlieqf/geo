import json
from pathlib import Path

from src.pipeline.question_generation import (
    DEFAULT_BRAND_QUESTION_COUNT,
    DEFAULT_QUESTION_COUNT,
    generate_question_draft,
    load_question_generation_config,
)


class StubAnalyzer:
    def __init__(self, payload: list[dict[str, str]]) -> None:
        self.payload = payload
        self.calls: list[dict[str, object]] = []

    def generate_text(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        return {
            "text": json.dumps(self.payload, ensure_ascii=False),
            "raw": {"ok": True},
        }


def test_generate_question_draft_saves_questions_and_metadata(tmp_path: Path) -> None:
    analyzer = StubAnalyzer(
        [
            {
                "question_id": "q1",
                "question_group": "generic",
                "intent_bucket": "direct_recommendation",
                "question": "中国 GEO 服务哪家强？",
                "why_this_question": "用户会直接问推荐",
            },
            {
                "question_id": "q2",
                "question_group": "brand_specific",
                "intent_bucket": "comparison_choice",
                "question": "流量玩家做中国 GEO 服务值不值得联系？",
                "why_this_question": "用户会对特定品牌做判断",
            },
        ]
    )

    result = generate_question_draft(
        keyword="中国 GEO 服务",
        brand="流量玩家",
        analyzer=analyzer,
        prompts_dir=Path("prompts"),
        storage_dir=tmp_path / "drafts",
    )

    assert analyzer.calls
    assert result["keyword"] == "中国 GEO 服务"
    assert result["brand"] == "流量玩家"
    assert result["question_count"] == 2
    assert result["configured_question_count"] == DEFAULT_QUESTION_COUNT
    assert result["configured_brand_question_count"] == DEFAULT_BRAND_QUESTION_COUNT
    assert Path(result["draft_path"]).exists()


def test_generate_question_draft_uses_default_question_count_and_brand_rules(
    tmp_path: Path,
) -> None:
    analyzer = StubAnalyzer(
        [
            {
                "question_id": "q1",
                "question_group": "generic",
                "intent_bucket": "direct_recommendation",
                "question": "test",
                "why_this_question": "test",
            }
        ]
    )

    generate_question_draft(
        keyword="中国 GEO 服务",
        brand="流量玩家",
        analyzer=analyzer,
        prompts_dir=Path("prompts"),
        storage_dir=tmp_path / "drafts",
    )

    assert analyzer.calls[0]["system_prompt"]
    assert str(DEFAULT_QUESTION_COUNT) in str(analyzer.calls[0]["system_prompt"])
    assert str(DEFAULT_BRAND_QUESTION_COUNT) in str(analyzer.calls[0]["system_prompt"])
    assert "流量玩家" in str(analyzer.calls[0]["user_prompt"])


def test_generate_question_draft_allows_overriding_question_count(
    tmp_path: Path,
) -> None:
    analyzer = StubAnalyzer(
        [
            {
                "question_id": "q1",
                "question_group": "generic",
                "intent_bucket": "direct_recommendation",
                "question": "test",
                "why_this_question": "test",
            }
        ]
    )

    result = generate_question_draft(
        keyword="中国 GEO 服务",
        brand="流量玩家",
        analyzer=analyzer,
        prompts_dir=Path("prompts"),
        storage_dir=tmp_path / "drafts",
        question_count=12,
    )

    assert result["configured_question_count"] == 12
    assert "12" in str(analyzer.calls[0]["system_prompt"])
    assert str(DEFAULT_BRAND_QUESTION_COUNT) in str(analyzer.calls[0]["system_prompt"])


def test_generate_question_draft_skips_brand_specific_generation_when_brand_empty(
    tmp_path: Path,
) -> None:
    analyzer = StubAnalyzer(
        [
            {
                "question_id": "q1",
                "question_group": "generic",
                "intent_bucket": "direct_recommendation",
                "question": "test",
                "why_this_question": "test",
            }
        ]
    )

    result = generate_question_draft(
        keyword="中国 GEO 服务",
        brand="",
        analyzer=analyzer,
        prompts_dir=Path("prompts"),
        storage_dir=tmp_path / "drafts",
    )

    assert result["brand"] == ""
    assert "品牌为空" in str(analyzer.calls[0]["user_prompt"])


def test_load_question_generation_config_reads_json_file() -> None:
    config = load_question_generation_config(Path("prompts"))

    assert config["default_question_count"] == 15
    assert config["brand_question_count"] >= 1
