from __future__ import annotations

from src.pipeline.discovery_run import DEFAULT_PROMPT_VARIANTS
from src.ui_copy import PROMPT_VARIANT_LABELS


INTERPRETATION_LABELS = {
    "geo_ai_optimization": "生成式引擎优化",
    "geo_geocoding": "地理编码",
    "geo_geofencing": "地理围栏",
    "geo_earth_observation": "地球观测",
    "unknown": "未知",
}

QUESTION_STATUS_LABELS = {
    "pending": "待运行",
    "running": "运行中",
    "completed": "已完成",
    "error": "失败",
    "cancelling": "停止中",
    "cancelled": "已停止",
}

QUESTION_STATUS_GLYPHS = {
    "pending": "○",
    "running": "◔",
    "completed": "●",
    "error": "✕",
    "cancelling": "◕",
    "cancelled": "■",
}


def question_table_height(row_count: int) -> int:
    if row_count <= 0:
        return 220
    estimated = 160 + row_count * 24
    return min(max(estimated, 220), 760)


def distillation_preview_height(row_count: int) -> int:
    if row_count <= 0:
        return 420
    estimated = 360 + row_count * 48
    return min(max(estimated, 420), 980)


def question_status_glyph(status: str) -> str:
    return QUESTION_STATUS_GLYPHS.get(status, QUESTION_STATUS_GLYPHS["pending"])


def question_status_label(status: str) -> str:
    return QUESTION_STATUS_LABELS.get(status, QUESTION_STATUS_LABELS["pending"])


def build_initial_question_progress(
    questions: list[dict[str, str]],
) -> dict[str, dict[str, object]]:
    progress: dict[str, dict[str, object]] = {}
    for question in questions:
        question_id = question["question_id"]
        progress[question_id] = {
            "question_id": question_id,
            "question_group": question.get("question_group", "generic"),
            "intent_bucket": question["intent_bucket"],
            "question": question["question"],
            "status": "pending",
            "completed_variants": 0,
            "total_variants": len(DEFAULT_PROMPT_VARIANTS),
            "answers": [],
        }
    return progress


def build_answer_trace_groups(
    questions: list[dict[str, object]],
    answers: list[dict[str, object]],
) -> list[dict[str, object]]:
    variant_order = {name: index for index, name in enumerate(PROMPT_VARIANT_LABELS)}
    answers_by_question: dict[str, list[dict[str, object]]] = {}
    for answer in answers:
        question_id = str(answer.get("question_id", "")).strip()
        if not question_id:
            continue
        answers_by_question.setdefault(question_id, []).append(answer)

    def ordered_answers(question_id: str) -> list[dict[str, object]]:
        rows = answers_by_question.get(question_id, [])
        return sorted(
            rows,
            key=lambda item: (
                variant_order.get(
                    str(item.get("prompt_variant", "")),
                    len(variant_order),
                ),
                str(item.get("prompt_variant", "")),
            ),
        )

    groups: list[dict[str, object]] = []
    seen_question_ids: set[str] = set()
    for question in questions:
        question_id = str(question.get("question_id", "")).strip()
        if not question_id:
            continue
        seen_question_ids.add(question_id)
        groups.append(
            {
                "question_id": question_id,
                "question_group": str(question.get("question_group", "generic")),
                "intent_bucket": str(question.get("intent_bucket", "")),
                "question": str(question.get("question", "")),
                "answers": ordered_answers(question_id),
            }
        )

    for question_id in sorted(answers_by_question):
        if question_id in seen_question_ids:
            continue
        fallback_answers = ordered_answers(question_id)
        first_answer = fallback_answers[0] if fallback_answers else {}
        groups.append(
            {
                "question_id": question_id,
                "question_group": str(first_answer.get("question_group", "generic")),
                "intent_bucket": str(first_answer.get("intent_bucket", "")),
                "question": str(first_answer.get("question", "")),
                "answers": fallback_answers,
            }
        )

    return groups


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def present_interpretation_label(label: str) -> str:
    return INTERPRETATION_LABELS.get(label, label or "未知")


def present_benchmark_summary(summary: dict[str, float]) -> list[dict[str, object]]:
    return [
        {
            "回答变体": PROMPT_VARIANT_LABELS.get(name, name),
            "网页相似度": score,
        }
        for name, score in summary.items()
    ]


def present_platform_scores(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    presented = []
    for row in rows:
        topics = _string_list(row.get("supporting_topics") or [])
        presented.append(
            {
                "平台": row.get("platform", ""),
                "主题数": len(topics),
                "信息熵": row.get("info_entropy_score", 0),
                "相关性": row.get("correlation_score", 0),
                "稳定性": row.get("stability_score", 0),
                "证据质量": row.get("evidence_quality_score", 0),
                "综合得分": row.get("final_score", 0),
                "机会分": row.get("niche_opportunity_score", 0),
            }
        )
    return presented


def present_niche_opportunities(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    presented = []
    for row in rows:
        presented.append(
            {
                "平台": row.get("platform", ""),
                "类型": row.get("platform_family", ""),
                "规模": row.get("size_tier", ""),
                "成本": row.get("cost_tier", ""),
                "机会分": row.get("niche_opportunity_score", 0),
                "值得做": row.get("why_it_matters", ""),
                "进入路径": row.get("entry_path", ""),
                "网址": row.get("verified_url") or row.get("official_url", ""),
                "链接校验": row.get("url_verification", "未校验"),
            }
        )
    return presented


def present_baseline_platforms(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    presented = []
    for row in rows:
        presented.append(
            {
                "平台": row.get("platform", ""),
                "类型": row.get("platform_family", ""),
                "综合得分": row.get("final_score", 0),
                "角色": "头部基线平台",
                "说明": row.get("why_low_competition", ""),
            }
        )
    return presented


def present_golden_set(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    presented = []
    for row in rows:
        new_topics = _string_list(row.get("new_topics", []))
        presented.append(
            {
                "平台": row.get("platform", ""),
                "新增覆盖": row.get("incremental_coverage", 0),
                "累计覆盖": row.get("cumulative_coverage", 0),
                "新增主题": "、".join(new_topics),
            }
        )
    return presented


def present_topic_units(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    presented = []
    for row in rows:
        supporting_domains = _string_list(row.get("supporting_domains", []))
        presented.append(
            {
                "主题": row.get("topic_label", ""),
                "判断": row.get("claim", ""),
                "置信度": row.get("confidence", 0),
                "支撑域名": "、".join(supporting_domains),
            }
        )
    return presented
