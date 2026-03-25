from src.pipeline.discovery_run import (
    DEFAULT_PROMPT_VARIANTS,
    _collect_source_signal_artifacts,
    _extract_promotable_platform_mentions,
    parse_question_pool_json,
    summarize_answer_batch,
)
from src.pipeline.platform_summary import summarize_actionable_platforms


def test_parse_question_pool_json_returns_question_rows() -> None:
    payload = """
    [
      {
        "question_id": "q_001",
        "intent_bucket": "direct_recommendation",
        "question": "中国 GEO 服务公司有哪些？",
        "why_this_question": "用户会直接问推荐"
      }
    ]
    """

    questions = parse_question_pool_json(payload)

    assert questions == [
        {
            "question_id": "q_001",
            "question_group": "generic",
            "intent_bucket": "direct_recommendation",
            "question": "中国 GEO 服务公司有哪些？",
            "why_this_question": "用户会直接问推荐",
        }
    ]


def test_parse_question_pool_json_accepts_object_with_questions_field() -> None:
    payload = """
    {
      "questions": [
        {
          "question_id": "q_001",
          "question_group": "generic",
          "intent_bucket": "direct_recommendation",
          "question": "中国 GEO 服务公司有哪些？",
          "why_this_question": "用户会直接问推荐"
        }
      ]
    }
    """

    questions = parse_question_pool_json(payload)

    assert questions == [
        {
            "question_id": "q_001",
            "question_group": "generic",
            "intent_bucket": "direct_recommendation",
            "question": "中国 GEO 服务公司有哪些？",
            "why_this_question": "用户会直接问推荐",
        }
    ]


def test_summarize_answer_batch_counts_sources_by_variant() -> None:
    summary = summarize_answer_batch(
        [
            {
                "prompt_variant": "natural",
                "text": "参考 https://zhihu.com/q/1",
                "urls": ["https://zhihu.com/q/1"],
                "domains": ["zhihu.com"],
                "source_labels": ["知乎"],
            },
            {
                "prompt_variant": "natural",
                "text": "没有明确来源",
                "urls": [],
                "domains": [],
                "source_labels": [],
            },
            {
                "prompt_variant": "source_seeking",
                "text": "来源包括 xiaohongshu.com",
                "urls": [],
                "domains": ["xiaohongshu.com"],
                "source_labels": ["小红书"],
            },
        ]
    )

    assert summary["natural"]["answer_count"] == 2
    assert summary["natural"]["answers_with_urls"] == 1
    assert summary["natural"]["answers_with_domains"] == 1
    assert summary["natural"]["answers_with_source_labels"] == 1
    assert summary["source_seeking"]["answers_with_domains"] == 1
    assert summary["source_seeking"]["answers_with_source_labels"] == 1


def test_collect_source_signal_artifacts_promotes_platform_mentions_to_actionable() -> (
    None
):
    artifacts = _collect_source_signal_artifacts(
        domains=["zhihu.com"],
        source_labels=["知乎"],
        platform_mentions=["站长之家", "雨果网"],
    )

    assert artifacts["actionable_platforms"] == ["知乎", "站长之家", "雨果网"]
    assert summarize_actionable_platforms(artifacts["unique_platform_signals"]) == [
        ("知乎", 1),
        ("站长之家", 1),
        ("雨果网", 1),
    ]


def test_extract_promotable_platform_mentions_skips_negative_baseline_references() -> (
    None
):
    mentions = _extract_promotable_platform_mentions(
        "知乎只作为基线参考，不建议当主阵地；更值得试的是站长之家和雨果网。"
    )

    assert mentions == ["站长之家", "雨果网"]


def test_default_prompt_variants_use_two_high_signal_modes() -> None:
    assert DEFAULT_PROMPT_VARIANTS == [
        "qwen_web_ranked_analysis",
        "qwen_web_source_emphasis",
    ]
