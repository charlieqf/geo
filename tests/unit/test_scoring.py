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


def test_build_platform_analysis_separates_baseline_and_niche_opportunities() -> None:
    answers = [
        {
            "question_id": "q1",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["36氪"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "行业趋势洞察",
                        "confidence": 0.94,
                        "evidence_span": "36氪适合做行业趋势洞察和头部曝光。",
                    }
                ]
            },
        },
        {
            "question_id": "q2",
            "intent_bucket": "comparison_choice",
            "prompt_variant": "web_source_emphasis",
            "actionable_platforms": ["IT之家"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "垂直科技口碑",
                        "confidence": 0.92,
                        "evidence_span": "IT之家更适合承接垂直科技口碑与长尾问题。",
                    }
                ]
            },
        },
        {
            "question_id": "q3",
            "intent_bucket": "risk_avoidance",
            "prompt_variant": "web_default",
            "actionable_platforms": ["V2EX"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "开发者真实反馈",
                        "confidence": 0.89,
                        "evidence_span": "V2EX适合发现真实反馈和低竞争问答切口。",
                    }
                ]
            },
        },
    ]

    analysis = build_platform_analysis(answers, target_coverage=0.85)

    assert [row["platform"] for row in analysis["baseline_platforms"]] == ["36氪"]
    assert [row["platform"] for row in analysis["niche_opportunities"]] == [
        "IT之家",
        "V2EX",
    ]
    assert all(row["size_tier"] != "head" for row in analysis["niche_opportunities"])
    assert all(
        row["niche_opportunity_score"] > 0 for row in analysis["niche_opportunities"]
    )


def test_build_platform_analysis_builds_niche_only_golden_set() -> None:
    answers = [
        {
            "question_id": "q1",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["知乎", "豆瓣"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "垂直讨论",
                        "confidence": 0.92,
                        "evidence_span": "豆瓣和知乎都可承接真实讨论。",
                    }
                ]
            },
        },
        {
            "question_id": "q2",
            "intent_bucket": "comparison_choice",
            "prompt_variant": "web_source_emphasis",
            "actionable_platforms": ["36氪", "CSDN"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "开发者实操",
                        "confidence": 0.9,
                        "evidence_span": "CSDN更适合承接开发者实操内容。",
                    }
                ]
            },
        },
    ]

    analysis = build_platform_analysis(answers, target_coverage=0.85)

    assert [row["platform"] for row in analysis["niche_golden_set"]] == [
        "豆瓣",
        "CSDN",
    ]
    assert all(
        row["platform"] not in {"知乎", "36氪"} for row in analysis["niche_golden_set"]
    )


def test_build_platform_analysis_penalizes_weak_evidence_and_preprocess_errors() -> (
    None
):
    answers = [
        {
            "question_id": "q1",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["CSDN"],
            "platform_mentions": ["CSDN"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "开发者口碑",
                        "confidence": 0.92,
                        "evidence_span": "CSDN适合承接开发者口碑和实操内容。",
                    }
                ],
                "noise_flags": {
                    "generic_listicle": False,
                    "weak_evidence": False,
                    "self_reference_only": False,
                },
            },
            "preprocess_error": None,
            "text": "CSDN适合承接开发者口碑和实操内容。",
        },
        {
            "question_id": "q2",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["V2EX"],
            "platform_mentions": ["V2EX"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "开发者口碑",
                        "confidence": 0.92,
                        "evidence_span": "V2EX适合承接开发者口碑和实操内容。",
                    }
                ],
                "noise_flags": {
                    "generic_listicle": True,
                    "weak_evidence": True,
                    "self_reference_only": False,
                },
            },
            "preprocess_error": None,
            "text": "V2EX适合承接开发者口碑和实操内容。",
        },
        {
            "question_id": "q3",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["豆瓣"],
            "platform_mentions": ["豆瓣"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "社区讨论",
                        "confidence": 0.92,
                        "evidence_span": "豆瓣适合承接社区讨论和长尾内容。",
                    }
                ],
                "noise_flags": {
                    "generic_listicle": False,
                    "weak_evidence": False,
                    "self_reference_only": False,
                },
            },
            "preprocess_error": None,
            "text": "豆瓣适合承接社区讨论和长尾内容。",
        },
        {
            "question_id": "q4",
            "intent_bucket": "effect_validation",
            "prompt_variant": "web_default",
            "actionable_platforms": ["豆瓣"],
            "platform_mentions": ["豆瓣"],
            "structured_analysis": None,
            "preprocess_error": "Unterminated string",
            "text": "豆瓣在这类问题里也被多次点名，但结构化失败。",
        },
    ]

    analysis = build_platform_analysis(answers, target_coverage=0.85)

    platform_scores = {row["platform"]: row for row in analysis["platform_scores"]}

    assert platform_scores["CSDN"]["evidence_quality_score"] == 1.0
    assert platform_scores["V2EX"]["evidence_quality_score"] < 1.0
    assert platform_scores["豆瓣"]["evidence_quality_score"] < 1.0
    assert (
        platform_scores["CSDN"]["final_score"] > platform_scores["V2EX"]["final_score"]
    )
    assert (
        platform_scores["CSDN"]["final_score"] > platform_scores["豆瓣"]["final_score"]
    )


def test_build_platform_analysis_does_not_penalize_incidental_platform_mentions() -> (
    None
):
    answers = [
        {
            "question_id": "q1",
            "intent_bucket": "direct_recommendation",
            "prompt_variant": "web_ranked_analysis",
            "actionable_platforms": ["CSDN"],
            "platform_mentions": ["CSDN"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "开发者实操",
                        "confidence": 0.9,
                        "evidence_span": "CSDN适合沉淀开发者实操内容。",
                    }
                ],
                "noise_flags": {
                    "generic_listicle": False,
                    "weak_evidence": False,
                    "self_reference_only": False,
                },
            },
            "preprocess_error": None,
        },
        {
            "question_id": "q2",
            "intent_bucket": "comparison_choice",
            "prompt_variant": "web_source_emphasis",
            "actionable_platforms": ["CSDN", "V2EX"],
            "platform_mentions": ["CSDN", "V2EX"],
            "structured_analysis": {
                "topic_units": [
                    {
                        "topic_label": "社区讨论",
                        "confidence": 0.88,
                        "evidence_span": "V2EX更适合承接社区讨论和问答切口。",
                    }
                ],
                "noise_flags": {
                    "generic_listicle": True,
                    "weak_evidence": True,
                    "self_reference_only": False,
                },
            },
            "preprocess_error": None,
        },
    ]

    analysis = build_platform_analysis(answers, target_coverage=0.85)

    platform_scores = {row["platform"]: row for row in analysis["platform_scores"]}

    assert platform_scores["CSDN"]["evidence_quality_score"] == 1.0
    assert platform_scores["V2EX"]["evidence_quality_score"] < 1.0
