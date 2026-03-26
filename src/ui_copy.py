from __future__ import annotations


APP_TITLE = "GEO 权重蒸馏机"

PROMPT_NAME_LABELS = {
    "question_pool_system": "问题池生成 · 系统提示词",
    "question_pool_user": "问题池生成 · 用户模板",
    "query_rewriter": "查询改写 · 用户模板",
    "qwen_web_default": "豆包网页行为 · 默认回答",
    "qwen_web_ranked_analysis": "豆包网页行为 · 分层盘点",
    "qwen_web_source_emphasis": "豆包网页行为 · 来源增强",
    "answer_structurer_system": "结构化预处理 · 系统提示词",
    "answer_structurer_user": "结构化预处理 · 用户模板",
    "topic_normalizer_system": "主题归一 · 系统提示词",
    "topic_normalizer_user": "主题归一 · 用户模板",
    "report_narrator_system": "结果解读 · 系统提示词",
    "report_narrator_user": "结果解读 · 用户模板",
}

PROMPT_VARIANT_LABELS = {
    "web_default": "默认回答",
    "web_ranked_analysis": "分层盘点",
    "web_source_emphasis": "来源增强",
}

PROMPT_VARIANT_EXPLANATIONS = {
    "web_ranked_analysis": "分层盘点：更强调排序与分层结构，以及平台优先级判断。",
    "web_source_emphasis": "来源增强：更强调来源显式度、证据暴露与后续抽取可用性。",
    "web_default": "默认回答：保持常规回答风格，用于一般性对照。",
}


HOME_PAGE = {
    "page_title": APP_TITLE,
    "hero_title": APP_TITLE,
    "hero_subtitle": "面向豆包搜索问答的 GEO 平台发现与权重分析工作台。",
    "kpi_target": "当前目标",
    "kpi_model": "分析模型",
    "kpi_runs": "实验记录",
    "workflow_title": "使用流程",
    "workflow_steps": [
        "在“蒸馏问题生成”输入关键词并生成问题池。",
        "在“运行蒸馏”选择问题池并调用豆包完成蒸馏。",
        "在“结果分析”查看高价值平台、平台评分与黄金集合。",
        "在“方法学说明”核对评分定义、过滤逻辑与局限性。",
    ],
    "advanced_settings_hint": "高级设置（提示词）只用于内部调参，不是普通用户的主流程入口。",
    "latest_runs_title": "最近实验",
    "no_runs": "暂无实验记录，请先运行一次实验。",
    "top_platforms_prefix": "高价值平台：",
}


PROMPT_LAB_PAGE = {
    "page_title": "高级设置（提示词）",
    "selector_label": "选择提示词",
    "heading": "高级设置（提示词）",
    "caption": "这里用于内部调参、调试和 Prompt 对比实验。普通用户通常不需要进入这个页面。",
    "editor_label": "提示词内容",
    "save_button": "保存提示词",
    "save_success": "已保存：{name}",
}


QUESTION_PAGE = {
    "page_title": "蒸馏问题生成",
    "heading": "蒸馏问题生成",
    "generator_tab": "问题生成",
    "prompt_tab": "生成 Prompt",
    "keyword_label": "关键词",
    "brand_label": "品牌（可选）",
    "question_count_label": "问题数量",
    "draft_selector": "选择问题池",
    "question_count_help": "默认 15 个通用问题；如果填写品牌，仍会额外生成 {brand_count} 个品牌相关问题。",
    "draft_title": "已生成问题池",
    "draft_empty": "还没有生成问题池，请先输入关键词并生成。",
    "draft_count": "问题数量",
    "draft_help": "默认展示最近一次生成的问题池，列表区域会尽量利用页面高度，方便连续浏览与校对。",
    "submit_label": "生成问题池",
    "spinner": "正在生成问题池，请稍候...",
    "success": "问题池生成完成。",
    "prompt_button": "查看问题池生成 Prompt",
    "prompt_system_title": "系统提示词",
    "prompt_user_title": "用户模板",
    "prompt_meta_title": "Prompt 配置",
}


DISTILL_PAGE = {
    "page_title": "运行蒸馏",
    "heading": "运行蒸馏",
    "draft_selector": "选择问题池",
    "draft_preview": "问题池预览",
    "status_panel_title": "运行状态",
    "control_panel_title": "运行控制",
    "ready_hint": "当前问题池已就绪，可以直接开始运行蒸馏。",
    "empty_state": "暂无可用问题池，请先到“蒸馏问题生成”创建。",
    "submit_label": "开始运行蒸馏",
    "spinner": "正在调用豆包执行蒸馏，请稍候...",
    "success": "蒸馏运行完成。",
    "progress_title": "蒸馏进度",
    "progress_summary": "已完成 {done}/{total} 个问题",
    "view_answers": "查看回答",
    "raw_answer_title": "回答原文",
    "raw_answer_empty": "该问题尚未生成回答。",
    "refresh_button": "刷新进度",
    "cancel_button": "停止蒸馏",
    "job_running": "后台任务正在运行。你可以切换到其他页面，回来后仍可恢复当前进度。",
    "job_cancelling": "后台任务正在停止，请稍候...",
    "job_cancelled": "后台蒸馏已停止。",
    "job_completed": "后台蒸馏已完成。",
    "job_error": "后台蒸馏失败。",
    "job_log_title": "运行日志",
    "job_log_empty": "当前还没有可显示的日志内容。",
}


RESULTS_PAGE = {
    "page_title": "结果分析",
    "heading": "结果分析",
    "empty_state": "暂无实验结果，请先到“运行实验”执行一次实验。",
    "run_selector": "选择实验",
    "niche_opportunities_title": "小平台机会榜",
    "baseline_platforms_title": "头部基线平台",
    "top_platforms_title": "高价值平台",
    "top_domains_title": "原始来源域名",
    "benchmark_title": "网页风格相似度",
    "platform_scores_title": "小平台机会评分",
    "golden_set_title": "小平台黄金集合",
    "baseline_scores_title": "头部基线参考",
    "answer_trace_title": "回答与证据追踪",
    "tab_overview": "总览",
    "tab_scores": "评分详情",
    "tab_trace": "回答追踪",
    "metric_niche_platforms": "小平台候选数",
    "metric_baseline_platforms": "头部基线平台数",
    "metric_best_niche_platform": "当前最佳小平台",
    "metric_best_niche_score": "最佳机会分",
    "score_metric_help": {
        "信息熵": "含义：某个平台相对当前平台集合带来的新增主题信息量。口径：按 supporting_topics 及其 topic_weights 汇总。计算：基于平台覆盖主题的加权熵，并结合稳定性校正。参考意义：越高，说明这个平台带来的不是重复信息，而是新的覆盖价值。",
        "相关性": "含义：某个平台与其他独立平台在同一主题上的互证强度。口径：按平台主题支持与总体 topic_weights 计算。计算：主题交集加权后再做稳定性校正。参考意义：越高，说明它不是孤证，而是被多个平台共同支撑。",
        "稳定性": "含义：该平台在不同问题、不同意图、不同回答变体中的重复出现程度。口径：综合问题覆盖率、意图覆盖率和变体覆盖率。计算：三个覆盖率取均值。参考意义：越高，说明这个平台不是偶然被提到，而是更稳定的机会。",
        "证据质量": "含义：该平台相关证据的可靠程度。口径：基于 weak_evidence、generic_listicle、preprocess_error 等标记。计算：从 1.0 起按噪音和失败情况降权。参考意义：越高，说明这条平台结论更值得信任。",
        "综合得分": "含义：平台证据层面的基础分。口径：只反映信息量、相关性和证据质量，不直接表达业务优先级。计算：先做 0.6×信息熵 + 0.4×相关性，再乘以证据质量。参考意义：适合解释平台证据强弱。",
        "机会分": "含义：面向业务决策的最终排序分。口径：在综合得分基础上，叠加平台垂直性、成本、进入路径等业务因素。计算：由 niche_opportunity_score 输出。参考意义：用于决定先做谁、后做谁。",
    },
    "golden_set_chart_title": "覆盖贡献趋势",
    "golden_set_chart_caption": "柱状表示每个平台带来的新增覆盖，折线表示累计覆盖；用于判断平台组合的边际贡献与整体收敛速度。",
    "caption_actionable": "高价值平台：{value}",
    "caption_urls": "链接：{value}",
    "caption_domains": "域名：{value}",
    "caption_structured": "语义解释：{interpretation} · 品牌可落地：{brand_grounded} · 来源显式度：{score}",
    "niche_empty": "当前结果里还没有足够明确的小平台机会。可通过更偏垂直、低竞争的问题池重跑一次。",
    "trace_summary": "共 {question_count} 个问题，已生成 {answer_count} 条回答记录。按问题分组后，每题可展开查看不同回答变体。",
    "trace_question_meta": "问题类型：{group} · 意图桶：{intent} · 回答变体数：{variant_count}",
    "trace_rewritten": "改写后的提问：{value}",
    "trace_variant_explanation": "变体说明：{value}",
    "trace_answer_empty": "该问题暂时没有可追踪的回答记录。",
    "trace_empty": "该回答尚未生成结构化分析。",
}


METHODOLOGY_PAGE = {
    "page_title": "方法学说明",
    "heading": "方法学说明",
    "body": """
**信息熵**：某个可投放信息平台相对当前平台集合带来的新增主题覆盖，并经过稳定性校正。

**相关性**：某个可投放信息平台与其他独立平台在同一主题上的互证强度，并经过稳定性校正。

**可投放信息平台**：客户可以真实运营内容的平台，如知乎、小红书、公众号、新闻媒体、论坛、博客/专栏和自有品牌阵地。

**证据来源**：回答中出现的任何来源线索。证据来源不会自动进入最终评分。

本系统明确区分：
- 证据来源
- 可投放信息平台

这样可以避免云厂商、基础设施文档和无运营意义的页面污染最终平台推荐结果。
""",
}
