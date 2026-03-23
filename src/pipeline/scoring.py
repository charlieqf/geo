from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from src.pipeline.golden_set import greedy_golden_set
from src.platform_registry import classify_source_signal, extract_platform_mentions


def _iter_topic_rows(answer_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for answer in answer_records:
        structured = answer.get("structured_analysis") or {}
        topic_units = structured.get("topic_units") or []
        platforms = answer.get("actionable_platforms") or []
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
        }

    topic_weights = _compute_topic_weights(topic_rows)
    platform_topics = _platform_support(topic_rows)
    prompt_variants = _platform_prompt_variants(topic_rows)
    intents = _platform_intents(topic_rows)
    questions = _platform_questions(topic_rows)

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
        final_score = round(0.6 * info_entropy_score + 0.4 * correlation_score, 4)

        row = {
            "platform": platform,
            "supporting_topics": sorted(topics),
            "topic_coverage_weight": topic_coverage_weight,
            "marginal_contribution": round(marginal_contribution, 4),
            "corroboration_strength": corroboration_strength,
            "stability_score": stability_score,
            "info_entropy_score": info_entropy_score,
            "correlation_score": correlation_score,
            "final_score": final_score,
        }
        platform_scores.append(row)
        final_scores_by_platform[platform] = final_score

    platform_scores.sort(key=lambda row: (-row["final_score"], row["platform"]))
    golden_set = greedy_golden_set(
        topic_weights=topic_weights,
        platform_topics=platform_topics,
        platform_scores=final_scores_by_platform,
        target_coverage=target_coverage,
    )

    return {
        "topic_weights": topic_weights,
        "platform_scores": platform_scores,
        "golden_set": golden_set,
    }
