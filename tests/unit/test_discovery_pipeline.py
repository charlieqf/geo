from src.pipeline.discovery_run import parse_question_pool_json, summarize_answer_batch


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
