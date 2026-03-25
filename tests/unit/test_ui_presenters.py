from src.ui_presenters import (
    build_answer_trace_groups,
    build_initial_question_progress,
    distillation_preview_height,
    present_baseline_platforms,
    question_table_height,
    question_status_glyph,
    question_status_label,
    present_benchmark_summary,
    present_golden_set,
    present_interpretation_label,
    present_niche_opportunities,
    present_platform_scores,
    present_topic_units,
)


def test_present_interpretation_label_returns_chinese_text() -> None:
    assert present_interpretation_label("geo_ai_optimization") == "生成式引擎优化"
    assert present_interpretation_label("unknown") == "未知"


def test_present_benchmark_summary_translates_variant_names() -> None:
    rows = present_benchmark_summary(
        {"web_ranked_analysis": 0.9, "web_source_emphasis": 0.5}
    )

    assert rows == [
        {"回答变体": "分层盘点", "网页相似度": 0.9},
        {"回答变体": "来源增强", "网页相似度": 0.5},
    ]


def test_present_platform_scores_uses_chinese_columns() -> None:
    rows = present_platform_scores(
        [
            {
                "platform": "知乎",
                "supporting_topics": ["高价值平台", "问答覆盖"],
                "info_entropy_score": 1.8,
                "correlation_score": 0.9,
                "stability_score": 0.8,
                "evidence_quality_score": 0.65,
                "final_score": 1.44,
                "niche_opportunity_score": 0.72,
            }
        ]
    )

    assert rows == [
        {
            "平台": "知乎",
            "主题数": 2,
            "信息熵": 1.8,
            "相关性": 0.9,
            "稳定性": 0.8,
            "证据质量": 0.65,
            "综合得分": 1.44,
            "机会分": 0.72,
        }
    ]


def test_present_golden_set_uses_chinese_columns() -> None:
    rows = present_golden_set(
        [
            {
                "platform": "知乎",
                "incremental_coverage": 0.75,
                "cumulative_coverage": 0.75,
                "new_topics": ["问答覆盖", "品牌解释"],
            }
        ]
    )

    assert rows == [
        {
            "平台": "知乎",
            "新增覆盖": 0.75,
            "累计覆盖": 0.75,
            "新增主题": "问答覆盖、品牌解释",
        }
    ]


def test_present_niche_opportunities_uses_business_columns() -> None:
    rows = present_niche_opportunities(
        [
            {
                "platform": "IT之家",
                "platform_family": "tech_media",
                "size_tier": "niche",
                "cost_tier": "medium",
                "niche_opportunity_score": 1.12,
                "why_it_matters": "覆盖垂直科技问答。",
                "entry_path": "投稿或栏目合作。",
                "official_url": "https://www.ithome.com",
                "verified_url": "https://www.ithome.com/articles",
                "url_verification": "可访问 (200)",
            }
        ]
    )

    assert rows == [
        {
            "平台": "IT之家",
            "类型": "tech_media",
            "规模": "niche",
            "成本": "medium",
            "机会分": 1.12,
            "值得做": "覆盖垂直科技问答。",
            "进入路径": "投稿或栏目合作。",
            "网址": "https://www.ithome.com/articles",
            "链接校验": "可访问 (200)",
        }
    ]


def test_present_baseline_platforms_uses_reference_columns() -> None:
    rows = present_baseline_platforms(
        [
            {
                "platform": "36氪",
                "platform_family": "tech_media",
                "final_score": 1.66,
                "why_low_competition": "属于头部综合媒体，适合作为基线参考。",
            }
        ]
    )

    assert rows == [
        {
            "平台": "36氪",
            "类型": "tech_media",
            "综合得分": 1.66,
            "角色": "头部基线平台",
            "说明": "属于头部综合媒体，适合作为基线参考。",
        }
    ]


def test_present_topic_units_uses_chinese_columns() -> None:
    rows = present_topic_units(
        [
            {
                "topic_label": "高价值平台",
                "claim": "知乎与小红书值得优先布局。",
                "confidence": 0.91,
                "supporting_domains": ["zhihu.com"],
            }
        ]
    )

    assert rows == [
        {
            "主题": "高价值平台",
            "判断": "知乎与小红书值得优先布局。",
            "置信度": 0.91,
            "支撑域名": "zhihu.com",
        }
    ]


def test_question_table_height_grows_with_row_count_and_caps() -> None:
    assert question_table_height(0) == 220
    assert question_table_height(5) > 220
    assert question_table_height(26) == 760
    assert question_table_height(80) == 760


def test_distillation_preview_height_prefers_taller_scroll_region() -> None:
    assert distillation_preview_height(0) == 420
    assert distillation_preview_height(8) > 700
    assert distillation_preview_height(20) == 980


def test_question_status_helpers_return_distinct_icons_and_labels() -> None:
    assert question_status_glyph("pending") == "○"
    assert question_status_glyph("running") == "◔"
    assert question_status_glyph("completed") == "●"
    assert question_status_glyph("error") == "✕"
    assert question_status_glyph("cancelled") == "■"
    assert question_status_label("pending") == "待运行"
    assert question_status_label("running") == "运行中"
    assert question_status_label("completed") == "已完成"
    assert question_status_label("error") == "失败"
    assert question_status_label("cancelled") == "已停止"


def test_build_initial_question_progress_sets_pending_state() -> None:
    rows = build_initial_question_progress(
        [
            {
                "question_id": "Q001",
                "question_group": "generic",
                "intent_bucket": "direct_recommendation",
                "question": "中国 GEO 服务哪家值得优先了解？",
            }
        ]
    )

    assert rows == {
        "Q001": {
            "question_id": "Q001",
            "question_group": "generic",
            "intent_bucket": "direct_recommendation",
            "question": "中国 GEO 服务哪家值得优先了解？",
            "status": "pending",
            "completed_variants": 0,
            "total_variants": 2,
            "answers": [],
        }
    }


def test_build_answer_trace_groups_keeps_question_order_and_variant_order() -> None:
    groups = build_answer_trace_groups(
        [
            {
                "question_id": "q1",
                "question_group": "generic",
                "intent_bucket": "direct_recommendation",
                "question": "问题一",
            },
            {
                "question_id": "q2",
                "question_group": "brand_specific",
                "intent_bucket": "brand_fit",
                "question": "问题二",
            },
        ],
        [
            {
                "question_id": "q1",
                "prompt_variant": "web_source_emphasis",
                "question": "问题一",
            },
            {
                "question_id": "q2",
                "prompt_variant": "web_ranked_analysis",
                "question": "问题二",
            },
            {
                "question_id": "q1",
                "prompt_variant": "web_default",
                "question": "问题一",
            },
        ],
    )

    assert [group["question_id"] for group in groups] == ["q1", "q2"]
    assert [answer["prompt_variant"] for answer in groups[0]["answers"]] == [
        "web_default",
        "web_source_emphasis",
    ]
    assert groups[1]["question_group"] == "brand_specific"


def test_build_answer_trace_groups_keeps_orphan_answers() -> None:
    groups = build_answer_trace_groups(
        [],
        [
            {
                "question_id": "q9",
                "prompt_variant": "web_default",
                "intent_bucket": "risk_avoidance",
                "question": "补充问题",
            }
        ],
    )

    assert groups == [
        {
            "question_id": "q9",
            "question_group": "generic",
            "intent_bucket": "risk_avoidance",
            "question": "补充问题",
            "answers": [
                {
                    "question_id": "q9",
                    "prompt_variant": "web_default",
                    "intent_bucket": "risk_avoidance",
                    "question": "补充问题",
                }
            ],
        }
    ]
