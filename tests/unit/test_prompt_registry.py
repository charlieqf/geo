from pathlib import Path

import pytest

from src.prompt_registry import PromptRegistry, PromptRenderError


def test_prompt_registry_lists_expected_prompts() -> None:
    registry = PromptRegistry(Path("prompts"))

    prompt_names = {definition.name for definition in registry.list_prompts()}

    assert {
        "question_pool_system",
        "question_pool_user",
        "query_rewriter",
        "qwen_web_default",
        "qwen_web_ranked_analysis",
        "qwen_web_source_emphasis",
        "answer_structurer_system",
        "answer_structurer_user",
        "topic_normalizer_system",
        "topic_normalizer_user",
        "report_narrator_system",
        "report_narrator_user",
    }.issubset(prompt_names)


def test_prompt_registry_renders_question_pool_template() -> None:
    registry = PromptRegistry(Path("prompts"))

    rendered = registry.render(
        "question_pool_user",
        {
            "keywords": "中国 GEO 服务",
            "brand": "流量玩家",
            "brand_instruction": "品牌：流量玩家\n请额外生成 6 个围绕该品牌的问题。",
        },
    )

    assert "中国 GEO 服务" in rendered
    assert "围绕这个关键词" in rendered
    assert "流量玩家" in rendered


def test_prompt_registry_raises_on_missing_variable() -> None:
    registry = PromptRegistry(Path("prompts"))

    with pytest.raises(PromptRenderError, match="keywords"):
        registry.render("question_pool_user", {})


def test_qwen_web_prompts_enforce_explicit_source_blocks() -> None:
    registry = PromptRegistry(Path("prompts"))

    prompts = {
        name: registry.get_prompt(name).content
        for name in (
            "qwen_web_default",
            "qwen_web_ranked_analysis",
            "qwen_web_source_emphasis",
        )
    }

    for content in prompts.values():
        assert "信息来源" in content
        assert "不要编造来源" in content
        assert "链接" in content
        assert "公开资料不足" in content


def test_qwen_web_prompts_prioritize_actionable_publish_platforms() -> None:
    registry = PromptRegistry(Path("prompts"))

    prompts = {
        name: registry.get_prompt(name).content
        for name in (
            "qwen_web_default",
            "qwen_web_ranked_analysis",
            "qwen_web_source_emphasis",
        )
    }

    for content in prompts.values():
        assert "知乎" in content
        assert "小红书" in content
        assert "新闻媒体" in content
        assert "论坛" in content
        assert "不要把云厂商官网" in content or "不要把云厂商" in content
