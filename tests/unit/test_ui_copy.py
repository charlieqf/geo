from src.ui_copy import (
    APP_TITLE,
    DISTILL_PAGE,
    HOME_PAGE,
    METHODOLOGY_PAGE,
    PROMPT_VARIANT_EXPLANATIONS,
    PROMPT_LAB_PAGE,
    QUESTION_PAGE,
    RESULTS_PAGE,
)


def test_ui_copy_is_fully_chinese_for_primary_navigation() -> None:
    assert APP_TITLE == "GEO 权重蒸馏机"
    assert HOME_PAGE["hero_title"] == "GEO 权重蒸馏机"
    assert PROMPT_LAB_PAGE["page_title"] == "高级设置（提示词）"
    assert QUESTION_PAGE["page_title"] == "蒸馏问题生成"
    assert DISTILL_PAGE["page_title"] == "运行蒸馏"
    assert RESULTS_PAGE["page_title"] == "结果分析"
    assert METHODOLOGY_PAGE["page_title"] == "方法学说明"


def test_ui_copy_uses_chinese_field_labels() -> None:
    assert QUESTION_PAGE["keyword_label"] == "关键词"
    assert QUESTION_PAGE["brand_label"] == "品牌（可选）"
    assert QUESTION_PAGE["draft_selector"] == "选择问题池"
    assert "15 个通用问题" in QUESTION_PAGE["question_count_help"]
    assert QUESTION_PAGE["prompt_button"] == "查看问题池生成 Prompt"
    assert DISTILL_PAGE["draft_selector"] == "选择问题池"
    assert DISTILL_PAGE["draft_preview"] == "问题池预览"
    assert DISTILL_PAGE["status_panel_title"] == "运行状态"
    assert DISTILL_PAGE["control_panel_title"] == "运行控制"
    assert "benchmark_file_label" not in DISTILL_PAGE
    assert RESULTS_PAGE["niche_opportunities_title"] == "小平台机会榜"
    assert RESULTS_PAGE["baseline_platforms_title"] == "头部基线平台"
    assert RESULTS_PAGE["golden_set_title"] == "小平台黄金集合"
    assert "信息熵" in RESULTS_PAGE["score_metric_help"]
    assert "累计覆盖" in RESULTS_PAGE["golden_set_chart_caption"]
    assert "排序与分层" in PROMPT_VARIANT_EXPLANATIONS["web_ranked_analysis"]
    assert "来源显式度" in PROMPT_VARIANT_EXPLANATIONS["web_source_emphasis"]
    assert HOME_PAGE["workflow_steps"][0] == "在“蒸馏问题生成”输入关键词并生成问题池。"
