from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from src.pipeline.golden_set import greedy_golden_set
from src.platform_registry import (
    classify_source_signal,
    extract_platform_mentions,
    get_platform_definition,
)


COMPETITION_PENALTIES = {
    "head": 0.9,
    "established": 0.2,
    "niche": 0.0,
    "owned": 0.0,
}

SPECIFICITY_SCORES = {
    "developer_community": 1.0,
    "forum": 0.75,
    "blog_media": 0.9,
    "tech_media": 1.0,
    "community": 0.7,
    "qa_community": 0.6,
    "lifestyle_community": 0.6,
    "wechat_media": 0.55,
    "media_platform": 0.55,
    "news_media": 0.45,
    "video_community": 0.45,
    "owned_media": 0.2,
}

AFFORDABILITY_SCORES = {
    "low": 1.0,
    "medium": 0.6,
    "high": 0.2,
}

ACTIONABILITY_SCORES = {
    "community_participation": 0.65,
    "content_operation": 0.8,
    "earned_media": 0.9,
    "owned_media": 0.4,
}

NICHE_EXCLUDED_PLATFORMS = {"品牌官网", "论坛", "博客/专栏"}
EVIDENCE_QUALITY_FLOOR = 0.35


def _metadata_for_platform(platform: str) -> dict[str, str]:
    definition = get_platform_definition(platform)
    if not definition:
        return {
            "platform_family": "unknown",
            "size_tier": "niche",
            "cost_tier": "medium",
            "actionability": "earned_media",
        }
    return {
        "platform_family": definition.platform_family or definition.platform_type,
        "size_tier": definition.size_tier,
        "cost_tier": definition.cost_tier,
        "actionability": definition.actionability,
    }


def _entry_path(actionability: str) -> str:
    mapping = {
        "community_participation": "优先从真实讨论、答疑和社区账号共建切入。",
        "content_operation": "优先用持续内容运营和账号矩阵逐步占位。",
        "earned_media": "优先尝试投稿、案例合作或栏目共创。",
        "owned_media": "优先通过自有阵地持续发布结构化内容。",
    }
    return mapping.get(actionability, "优先从低成本内容试投和小规模合作切入。")


def _why_low_competition(size_tier: str, platform_family: str) -> str:
    if size_tier == "head":
        return "属于头部综合平台，适合作为基线参考。"
    if platform_family in {"developer_community", "forum", "blog_media"}:
        return "垂直属性更强、投放与内容竞争通常低于头部综合媒体。"
    if platform_family in {"tech_media", "community"}:
        return "相对更垂直，进入门槛和同行挤压通常低于头部大媒体。"
    return "不是标准头部流量入口，更适合发现低竞争切口。"


def _risk_notes(platform_family: str) -> str:
    if platform_family in {"forum", "community", "developer_community"}:
        return "用户讨论质量波动较大，需要人工筛选高质量切口。"
    if platform_family in {"tech_media", "news_media", "blog_media"}:
        return "依赖编辑与栏目偏好，合作稳定性和规模需逐个平台验证。"
    return "需要持续跟踪来源质量，避免把短期热度误判为长期机会。"


def _why_it_matters(topics: set[str]) -> str:
    ordered_topics = sorted(topics)
    if not ordered_topics:
        return "在当前问题池里出现了稳定的可布局信号。"
    focus = "、".join(ordered_topics[:2])
    return f"在当前问题池里反复支撑 {focus} 等主题。"


def _iter_topic_rows(answer_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for answer in answer_records:
        structured = answer.get("structured_analysis") or {}
        topic_units = structured.get("topic_units") or []
        if not topic_units:
            continue
        for topic_unit in topic_units:
            inferred_platforms: set[str] = set()
            for supporting_domain in topic_unit.get("supporting_domains", []) or []:
                classified = classify_source_signal(
                    domain=str(supporting_domain), source_label=None
                )
                if classified.is_actionable_platform and classified.normalized_platform:
                    inferred_platforms.add(classified.normalized_platform)

            evidence_text = " ".join(
                filter(
                    None,
                    [
                        str(topic_unit.get("topic_label", "")),
                        str(topic_unit.get("claim", "")),
                        str(topic_unit.get("evidence_span", "")),
                    ],
                )
            )
            for platform_name in extract_platform_mentions(evidence_text):
                classified = classify_source_signal(
                    domain=None, source_label=platform_name
                )
                if classified.is_actionable_platform and classified.normalized_platform:
                    inferred_platforms.add(classified.normalized_platform)

            if not inferred_platforms:
                continue

            rows.append(
                {
                    "question_id": answer.get("question_id"),
                    "intent_bucket": answer.get("intent_bucket"),
                    "prompt_variant": answer.get("prompt_variant"),
                    "platforms": sorted(inferred_platforms),
                    "topic_label": str(topic_unit.get("topic_label")),
                    "confidence": float(topic_unit.get("confidence", 0.0)),
                }
            )
    return rows


def _answer_evidence_quality(answer: dict[str, Any]) -> float:
    structured = answer.get("structured_analysis") or {}
    noise_flags = structured.get("noise_flags") or {}

    quality = 1.0
    if bool(noise_flags.get("weak_evidence")):
        quality -= 0.2
    if bool(noise_flags.get("generic_listicle")):
        quality -= 0.15
    if answer.get("preprocess_error"):
        quality -= 0.25

    return round(max(EVIDENCE_QUALITY_FLOOR, quality), 4)


def _collect_answer_platform_candidates(answer: dict[str, Any]) -> set[str]:
    candidates: set[str] = set()
    structured = answer.get("structured_analysis") or {}
    topic_units = structured.get("topic_units") or []
    for topic_unit in topic_units:
        for supporting_domain in topic_unit.get("supporting_domains", []) or []:
            classified = classify_source_signal(
                domain=str(supporting_domain), source_label=None
            )
            if classified.is_actionable_platform and classified.normalized_platform:
                candidates.add(classified.normalized_platform)

        evidence_text = " ".join(
            filter(
                None,
                [
                    str(topic_unit.get("topic_label", "")),
                    str(topic_unit.get("claim", "")),
                    str(topic_unit.get("evidence_span", "")),
                ],
            )
        )
        for platform_name in extract_platform_mentions(evidence_text):
            classified = classify_source_signal(domain=None, source_label=platform_name)
            if classified.is_actionable_platform and classified.normalized_platform:
                candidates.add(classified.normalized_platform)

    if candidates or topic_units:
        return candidates

    candidates.update(
        str(platform)
        for platform in answer.get("actionable_platforms") or []
        if str(platform).strip()
    )

    for platform_name in answer.get("platform_mentions") or []:
        classified = classify_source_signal(
            domain=None, source_label=str(platform_name)
        )
        if classified.is_actionable_platform and classified.normalized_platform:
            candidates.add(classified.normalized_platform)

    return candidates


def _platform_evidence_quality(
    answer_records: list[dict[str, Any]],
) -> dict[str, float]:
    scores: dict[str, list[float]] = defaultdict(list)
    for answer in answer_records:
        quality = _answer_evidence_quality(answer)
        for platform in _collect_answer_platform_candidates(answer):
            scores[platform].append(quality)

    return {
        platform: round(mean(platform_scores), 4)
        for platform, platform_scores in scores.items()
    }


def _compute_topic_weights(topic_rows: list[dict[str, Any]]) -> dict[str, float]:
    total_questions = len({row["question_id"] for row in topic_rows}) or 1
    total_intents = len({row["intent_bucket"] for row in topic_rows}) or 1

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in topic_rows:
        grouped[row["topic_label"]].append(row)

    weights: dict[str, float] = {}
    for topic_label, rows in grouped.items():
        question_coverage = len({row["question_id"] for row in rows}) / total_questions
        intent_coverage = len({row["intent_bucket"] for row in rows}) / total_intents
        avg_confidence = mean(row["confidence"] for row in rows)
        weights[topic_label] = round(
            0.5 * question_coverage + 0.3 * intent_coverage + 0.2 * avg_confidence,
            4,
        )
    return weights


def _platform_support(topic_rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    support: dict[str, set[str]] = defaultdict(set)
    for row in topic_rows:
        for platform in row["platforms"]:
            support[platform].add(row["topic_label"])
    return support


def _platform_prompt_variants(topic_rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    variants: dict[str, set[str]] = defaultdict(set)
    for row in topic_rows:
        for platform in row["platforms"]:
            variants[platform].add(str(row.get("prompt_variant")))
    return variants


def _platform_intents(topic_rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    intents: dict[str, set[str]] = defaultdict(set)
    for row in topic_rows:
        for platform in row["platforms"]:
            intents[platform].add(str(row.get("intent_bucket")))
    return intents


def _platform_questions(topic_rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    questions: dict[str, set[str]] = defaultdict(set)
    for row in topic_rows:
        for platform in row["platforms"]:
            questions[platform].add(str(row.get("question_id")))
    return questions


def build_platform_analysis(
    answer_records: list[dict[str, Any]], target_coverage: float = 0.85
) -> dict[str, Any]:
    topic_rows = _iter_topic_rows(answer_records)
    if not topic_rows:
        return {
            "topic_weights": {},
            "platform_scores": [],
            "golden_set": [],
            "baseline_platforms": [],
            "niche_opportunities": [],
            "niche_golden_set": [],
        }

    topic_weights = _compute_topic_weights(topic_rows)
    platform_topics = _platform_support(topic_rows)
    prompt_variants = _platform_prompt_variants(topic_rows)
    intents = _platform_intents(topic_rows)
    questions = _platform_questions(topic_rows)
    evidence_quality_scores = _platform_evidence_quality(answer_records)

    total_prompt_variants = (
        len({str(answer.get("prompt_variant")) for answer in answer_records}) or 1
    )
    total_intents = (
        len({str(answer.get("intent_bucket")) for answer in answer_records}) or 1
    )
    total_questions = (
        len({str(answer.get("question_id")) for answer in answer_records}) or 1
    )

    platform_scores: list[dict[str, Any]] = []
    final_scores_by_platform: dict[str, float] = {}

    for platform in sorted(platform_topics):
        metadata = _metadata_for_platform(platform)
        topics = platform_topics[platform]
        topic_coverage_weight = round(sum(topic_weights[topic] for topic in topics), 4)

        other_platforms = {
            other: other_topics
            for other, other_topics in platform_topics.items()
            if other != platform
        }
        corroboration_samples = []
        for topic in topics:
            other_support_count = sum(
                1 for other_topics in other_platforms.values() if topic in other_topics
            )
            corroboration_samples.append(
                min(1.0, 0.5 + 0.25 * other_support_count)
                if other_support_count
                else 0.0
            )
        corroboration_strength = round(
            mean(corroboration_samples) if corroboration_samples else 0.0, 4
        )

        prompt_consistency = (
            len(prompt_variants.get(platform, set())) / total_prompt_variants
        )
        intent_breadth = len(intents.get(platform, set())) / total_intents
        question_breadth = len(questions.get(platform, set())) / total_questions
        stability_score = round(
            0.5 * prompt_consistency + 0.3 * intent_breadth + 0.2 * question_breadth, 4
        )

        marginal_contribution = topic_coverage_weight
        info_entropy_score = round(
            marginal_contribution * (0.7 + 0.3 * stability_score), 4
        )
        correlation_score = round(
            corroboration_strength * (0.7 + 0.3 * stability_score), 4
        )
        evidence_quality_score = evidence_quality_scores.get(platform, 1.0)
        final_score = round(
            (0.6 * info_entropy_score + 0.4 * correlation_score)
            * evidence_quality_score,
            4,
        )
        specificity_score = SPECIFICITY_SCORES.get(metadata["platform_family"], 0.5)
        affordability_score = AFFORDABILITY_SCORES.get(metadata["cost_tier"], 0.5)
        actionability_score = ACTIONABILITY_SCORES.get(metadata["actionability"], 0.5)
        competition_penalty = COMPETITION_PENALTIES.get(metadata["size_tier"], 0.0)
        niche_opportunity_score = round(
            max(
                0.0,
                0.55 * final_score
                + 0.2 * specificity_score
                + 0.15 * affordability_score
                + 0.1 * actionability_score
                - competition_penalty,
            ),
            4,
        )

        row = {
            "platform": platform,
            "platform_family": metadata["platform_family"],
            "size_tier": metadata["size_tier"],
            "cost_tier": metadata["cost_tier"],
            "actionability": metadata["actionability"],
            "supporting_topics": sorted(topics),
            "topic_coverage_weight": topic_coverage_weight,
            "marginal_contribution": round(marginal_contribution, 4),
            "corroboration_strength": corroboration_strength,
            "stability_score": stability_score,
            "info_entropy_score": info_entropy_score,
            "correlation_score": correlation_score,
            "evidence_quality_score": evidence_quality_score,
            "final_score": final_score,
            "competition_penalty": competition_penalty,
            "niche_opportunity_score": niche_opportunity_score,
            "why_it_matters": _why_it_matters(topics),
            "why_low_competition": _why_low_competition(
                metadata["size_tier"], metadata["platform_family"]
            ),
            "entry_path": _entry_path(metadata["actionability"]),
            "risk_notes": _risk_notes(metadata["platform_family"]),
        }
        platform_scores.append(row)
        final_scores_by_platform[platform] = final_score

    platform_scores.sort(key=lambda row: (-row["final_score"], row["platform"]))
    baseline_platforms = [
        row for row in platform_scores if row.get("size_tier") == "head"
    ]
    niche_opportunities = [
        row
        for row in platform_scores
        if row.get("size_tier") != "head"
        and row.get("platform") not in NICHE_EXCLUDED_PLATFORMS
        and row.get("platform_family") != "owned_media"
    ]
    niche_opportunities.sort(
        key=lambda row: (
            -row["niche_opportunity_score"],
            -row["final_score"],
            row["platform"],
        )
    )
    niche_platform_names = {row["platform"] for row in niche_opportunities}
    niche_platform_topics = {
        platform: topics
        for platform, topics in platform_topics.items()
        if platform in niche_platform_names
    }
    niche_topic_names = {
        topic for topics in niche_platform_topics.values() for topic in topics
    }
    niche_topic_weights = {
        topic: weight
        for topic, weight in topic_weights.items()
        if topic in niche_topic_names
    }
    niche_scores_by_platform = {
        row["platform"]: row["niche_opportunity_score"] for row in niche_opportunities
    }
    golden_set = greedy_golden_set(
        topic_weights=topic_weights,
        platform_topics=platform_topics,
        platform_scores=final_scores_by_platform,
        target_coverage=target_coverage,
    )
    niche_golden_set = (
        greedy_golden_set(
            topic_weights=niche_topic_weights,
            platform_topics=niche_platform_topics,
            platform_scores=niche_scores_by_platform,
            target_coverage=target_coverage,
        )
        if niche_platform_topics and niche_topic_weights
        else []
    )

    return {
        "topic_weights": topic_weights,
        "platform_scores": platform_scores,
        "golden_set": golden_set,
        "baseline_platforms": baseline_platforms,
        "niche_opportunities": niche_opportunities,
        "niche_golden_set": niche_golden_set,
    }
