from src.pipeline.scoring import build_platform_analysis


def test_build_platform_analysis_scores_unique_and_corroborated_topics() -> None:
    answers = [
        {
            "question_id": "q1",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["知乎"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "权威问答覆盖",
                        "confidence": 0.95,
                        "evidence_span": "知乎问答内容覆盖核心品牌问题。",
                    }
                ]
            },
        },
        {
            "question_id": "q2",
            "intent_bucket": "case_reputation",
            "prompt_variant": "web_source_emphasis",
            "actionable_platforms": ["小红书"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "案例种草扩散",
                        "confidence": 0.92,
                        "evidence_span": "小红书笔记和案例内容更适合种草扩散。",
                    }
                ]
            },
        },
        {
            "question_id": "q3",
            "intent_bucket": "comparison_choice",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["知乎", "IT之家"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "科技媒体背书",
                        "confidence": 0.88,
                        "evidence_span": "知乎与IT之家都适合承接科技媒体背书。",
                    }
                ]
            },
        },
        {
            "question_id": "q4",
            "intent_bucket": "comparison_choice",
            "prompt_variant": "web_default",
            "actionable_platforms": ["IT之家"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "科技媒体背书",
                        "confidence": 0.83,
                        "evidence_span": "IT之家能提供媒体背书。",
                    }
                ]
            },
        },
    ]

    analysis = build_platform_analysis(answers, target_coverage=0.85)

    platform_scores = {row["platform"]: row for row in analysis["platform_scores"]}

    assert set(platform_scores) == {"知乎", "小红书", "IT之家"}
    assert (
        platform_scores["知乎"]["info_entropy_score"]
        > platform_scores["IT之家"]["info_entropy_score"]
    )
    assert platform_scores["IT之家"]["correlation_score"] > 0
    assert platform_scores["小红书"]["marginal_contribution"] > 0


def test_build_platform_analysis_returns_golden_set_by_weighted_coverage() -> None:
    answers = [
        {
            "question_id": "q1",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["知乎"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "权威问答覆盖",
                        "confidence": 0.95,
                        "evidence_span": "知乎问答内容覆盖核心品牌问题。",
                    },
                    {
                        "topic_label": "科技媒体背书",
                        "confidence": 0.9,
                        "evidence_span": "知乎与IT之家形成媒体与问答协同。",
                    },
                ]
            },
        },
        {
            "question_id": "q2",
            "intent_bucket": "case_reputation",
            "prompt_variant": "web_source_emphasis",
            "actionable_platforms": ["小红书"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "案例种草扩散",
                        "confidence": 0.92,
                        "evidence_span": "小红书案例内容推动种草扩散。",
                    }
                ]
            },
        },
        {
            "question_id": "q3",
            "intent_bucket": "comparison_choice",
            "prompt_variant": "web_default",
            "actionable_platforms": ["IT之家"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "科技媒体背书",
                        "confidence": 0.84,
                        "evidence_span": "IT之家媒体内容强化科技背书。",
                    }
                ]
            },
        },
    ]

    analysis = build_platform_analysis(answers, target_coverage=0.85)

    golden_set = analysis["golden_set"]

    assert [item["platform"] for item in golden_set] == ["知乎", "小红书"]
    assert golden_set[-1]["cumulative_coverage"] >= 0.85


def test_build_platform_analysis_uses_topic_rows_for_stability() -> None:
    answers = [
        {
            "question_id": "q1",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_default",
            "actionable_platforms": ["知乎"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "问答覆盖",
                        "confidence": 0.95,
                        "evidence_span": "知乎适合承接专业问答。",
                    }
                ]
            },
        },
        {
            "question_id": "q2",
            "intent_bucket": "risk_avoidance",
            "prompt_variant": "web_source_emphasis",
            "actionable_platforms": ["知乎"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "服务商避坑",
                        "confidence": 0.9,
                        "evidence_span": "采购前要核验案例与合同条款。",
                    }
                ]
            },
        },
    ]

    analysis = build_platform_analysis(answers, target_coverage=0.85)

    zhihu = next(
        row for row in analysis["platform_scores"] if row["platform"] == "知乎"
    )

    assert zhihu["stability_score"] < 1.0
