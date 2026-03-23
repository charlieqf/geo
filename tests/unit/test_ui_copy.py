from src.ui_copy import (
    APP_TITLE,
    DISTILL_PAGE,
    HOME_PAGE,
    METHODOLOGY_PAGE,
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
    assert QUESTION_PAGE["prompt_button"] == "查看问题池生成 Prompt"
    assert DISTILL_PAGE["draft_selector"] == "选择问题池"
    assert RESULTS_PAGE["top_platforms_title"] == "高价值平台"
    assert RESULTS_PAGE["golden_set_title"] == "黄金集合"
    assert HOME_PAGE["workflow_steps"][0] == "在“蒸馏问题生成”输入关键词并生成问题池。"
