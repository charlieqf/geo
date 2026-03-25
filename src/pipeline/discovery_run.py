from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from src.config import AppConfig
from src.pipeline.answer_preprocess import (
    analyze_answer_record,
    structured_payload_to_dict,
)
from src.pipeline.benchmark_evaluator import (
    extract_behavior_features,
    score_against_benchmark,
)
from src.pipeline.platform_summary import summarize_actionable_platforms
from src.pipeline.scoring import build_platform_analysis
from src.platform_registry import (
    ClassifiedSourceSignal,
    build_platform_index,
    classify_source_signal,
)
from src.prompt_registry import PromptRegistry
from src.providers.openai_client import OpenAIAnalysisClient
from src.providers.qwen_client import QwenChatClient
from src.utils.time_utils import utc_now_iso
from src.utils.url_utils import extract_domains, extract_source_labels, extract_urls


DEFAULT_INTENT_BUCKETS = [
    "direct_recommendation",
    "comparison_choice",
    "risk_avoidance",
    "effect_validation",
    "case_reputation",
]

DEFAULT_PROMPT_VARIANTS = [
    "qwen_web_ranked_analysis",
    "qwen_web_source_emphasis",
]
NEGATIVE_MENTION_PREFIXES = (
    "不建议",
    "不推荐",
    "不要",
    "避免",
    "排除",
    "除外",
    "不宜",
    "不适合",
    "不算",
    "别在",
)
BASELINE_MENTION_PREFIXES = (
    "作为基线",
    "只作基线",
    "仅作基线",
    "作为参考",
    "只作参考",
    "仅作参考",
    "作为对照",
)
COMPARATIVE_MENTION_PREFIXES = ("相比", "对比", "相较于", "相对于")
POSITIVE_MENTION_NEARBY = (
    "推荐",
    "适合",
    "值得",
    "优先",
    "可做",
    "可试",
    "机会",
    "切口",
)


class DistillationCancelledError(RuntimeError):
    """Raised when a background distillation job is cancelled."""


def build_target_client_settings(config: AppConfig) -> dict[str, str]:
    if not config.doubao_api_key:
        raise ValueError("DOUBAO_API_KEY is required for the active target provider")
    return {
        "provider": "doubao",
        "api_key": config.doubao_api_key,
        "base_url": config.doubao_base_url,
        "model": config.doubao_model,
    }


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def parse_question_pool_json(text: str) -> list[dict[str, str]]:
    payload = json.loads(_strip_code_fences(text))
    if isinstance(payload, dict):
        payload = payload.get("questions")
    if not isinstance(payload, list):
        raise ValueError("Question pool payload must be a JSON array")

    questions: list[dict[str, str]] = []
    for item in payload:
        questions.append(
            {
                "question_id": str(item["question_id"]),
                "question_group": str(item.get("question_group", "generic")),
                "intent_bucket": str(item["intent_bucket"]),
                "question": str(item["question"]),
                "why_this_question": str(item["why_this_question"]),
            }
        )
    return questions


def summarize_answer_batch(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for record in records:
        variant = str(record["prompt_variant"])
        variant_summary = summary.setdefault(
            variant,
            {
                "answer_count": 0,
                "answers_with_urls": 0,
                "answers_with_domains": 0,
                "answers_with_source_labels": 0,
            },
        )
        variant_summary["answer_count"] += 1
        if record.get("urls"):
            variant_summary["answers_with_urls"] += 1
        if record.get("domains"):
            variant_summary["answers_with_domains"] += 1
        if record.get("source_labels"):
            variant_summary["answers_with_source_labels"] += 1
    return summary


def _is_promotable_platform_match(text: str, start: int, end: int) -> bool:
    before = text[max(0, start - 12) : start]
    after = text[end : min(len(text), end + 12)]
    nearby = before + after

    if any(token in nearby for token in NEGATIVE_MENTION_PREFIXES):
        return False
    if any(token in before for token in COMPARATIVE_MENTION_PREFIXES):
        return False
    if any(token in nearby for token in BASELINE_MENTION_PREFIXES) and not any(
        token in nearby for token in POSITIVE_MENTION_NEARBY
    ):
        return False
    return True


def _extract_promotable_platform_mentions(text: str) -> list[str]:
    mentions: set[str] = set()
    aliases = sorted(
        build_platform_index().by_name.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for alias, definition in aliases:
        if not alias:
            continue
        for match in re.finditer(re.escape(alias), text, flags=re.IGNORECASE):
            if _is_promotable_platform_match(text, match.start(), match.end()):
                mentions.add(definition.display_name)
                break
    return sorted(mentions)


def _build_classified_source_entry(
    *, domain: str | None, source_label: str | None
) -> dict[str, Any]:
    return {
        "domain": domain,
        "source_label": source_label,
        **asdict(classify_source_signal(domain=domain, source_label=source_label)),
    }


def _collect_source_signal_artifacts(
    *,
    domains: list[str],
    source_labels: list[str],
    platform_mentions: list[str],
) -> dict[str, Any]:
    classified_sources: list[dict[str, Any]] = []
    candidate_sources: list[dict[str, Any]] = []

    for domain in domains:
        entry = _build_classified_source_entry(domain=domain, source_label=None)
        classified_sources.append(entry)
        candidate_sources.append(entry)

    for source_label in source_labels:
        entry = _build_classified_source_entry(domain=None, source_label=source_label)
        classified_sources.append(entry)
        candidate_sources.append(entry)

    for platform_name in platform_mentions:
        entry = _build_classified_source_entry(domain=None, source_label=platform_name)
        classified_sources.append(entry)
        candidate_sources.append(entry)

    actionable_platforms = sorted(
        {
            item["normalized_platform"]
            for item in candidate_sources
            if item["is_actionable_platform"] and item["normalized_platform"]
        }
    )

    unique_platform_signals: dict[str, ClassifiedSourceSignal] = {}
    for item in candidate_sources:
        key = (
            item["normalized_platform"]
            or f"unknown:{item['domain'] or item['source_label'] or 'none'}"
        )
        unique_platform_signals[key] = classify_source_signal(
            domain=item["domain"], source_label=item["source_label"]
        )

    return {
        "classified_sources": classified_sources,
        "actionable_platforms": actionable_platforms,
        "unique_platform_signals": list(unique_platform_signals.values()),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_discovery_notes(
    *,
    keyword: str,
    question_count: int,
    variant_summary: dict[str, dict[str, int]],
    top_domains: list[tuple[str, int]],
    top_actionable_platforms: list[tuple[str, int]],
    benchmark_summary: dict[str, float],
) -> str:
    lines = [
        f"# Doubao Discovery Notes - {keyword}",
        "",
        f"- Question count: `{question_count}`",
        f"- Prompt variants tested: `{', '.join(sorted(variant_summary))}`",
        "",
        "## Variant Summary",
        "",
    ]
    for variant, stats in variant_summary.items():
        lines.append(
            f"- `{variant}`: answers={stats['answer_count']}, with_urls={stats['answers_with_urls']}, with_domains={stats['answers_with_domains']}, with_source_labels={stats['answers_with_source_labels']}, avg_web_benchmark_score={benchmark_summary.get(variant, 0):.3f}"
        )
    lines.extend(["", "## Top Domains", ""])
    if top_domains:
        for domain, count in top_domains[:15]:
            lines.append(f"- `{domain}`: {count}")
    else:
        lines.append("- No explicit domains extracted.")
    lines.extend(["", "## Top Actionable Platforms", ""])
    if top_actionable_platforms:
        for platform_name, count in top_actionable_platforms[:15]:
            lines.append(f"- `{platform_name}`: {count}")
    else:
        lines.append("- No actionable publishing platforms extracted.")
    lines.extend(
        [
            "",
            "## Initial Assessment",
            "",
            "- Use this run to inspect whether Qwen tends to provide explicit citations, implicit brand mentions, or generic listicle-style answers.",
            "- Compare prompt variants by how often they yield extractable sources and concrete decision criteria.",
            "- Feed the raw answers into the next prompt iteration before locking the production prompt set.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_discovery(
    *,
    config: AppConfig,
    keyword: str,
    questions: list[dict[str, str]],
    benchmark_text: str | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    registry = PromptRegistry(config.prompts_dir)
    openai_client = OpenAIAnalysisClient(
        config.openai_api_key or "", config.openai_model
    )
    target_settings = build_target_client_settings(config)
    qwen_client = QwenChatClient(
        target_settings["api_key"],
        target_settings["base_url"],
        target_settings["model"],
    )
    answer_structurer_system = registry.get_prompt("answer_structurer_system").content
    answer_structurer_user = registry.get_prompt("answer_structurer_user").content

    run_id = f"discovery-{keyword.replace(' ', '-').replace('/', '-')}-{utc_now_iso().replace(':', '-')}"
    run_dir = config.runs_dir / run_id
    raw_dir = run_dir / "raw_answers"
    _write_json(run_dir / "questions.json", questions)

    benchmark_features = (
        extract_behavior_features(benchmark_text) if benchmark_text else None
    )

    answers: list[dict[str, Any]] = []
    domain_counts: dict[str, int] = {}
    all_classified_signals = []
    benchmark_scores_by_variant: dict[str, list[float]] = {}
    for question in questions:
        if should_cancel and should_cancel():
            raise DistillationCancelledError("Distillation job cancelled by user")
        current_question_answers: list[dict[str, Any]] = []
        if progress_callback:
            progress_callback(
                {
                    "question_id": question["question_id"],
                    "question_group": question.get("question_group", "generic"),
                    "intent_bucket": question["intent_bucket"],
                    "question": question["question"],
                    "status": "running",
                    "completed_variants": 0,
                    "total_variants": len(DEFAULT_PROMPT_VARIANTS),
                    "answers": [],
                }
            )
        rewritten_question = openai_client.generate_text(
            system_prompt=None,
            user_prompt=registry.render(
                "query_rewriter", {"question": question["question"]}
            ),
            temperature=0.1,
            max_output_tokens=400,
        )["text"].strip()
        for prompt_name in DEFAULT_PROMPT_VARIANTS:
            if should_cancel and should_cancel():
                raise DistillationCancelledError("Distillation job cancelled by user")
            prompt_variant = prompt_name.replace("qwen_", "")
            user_prompt = registry.render(prompt_name, {"question": rewritten_question})
            try:
                result = qwen_client.generate_text(
                    system_prompt=None, user_prompt=user_prompt
                )
                urls = extract_urls(result["text"])
                domains = extract_domains(result["text"])
                source_labels = extract_source_labels(result["text"])
                platform_mentions = _extract_promotable_platform_mentions(
                    result["text"]
                )
                source_signal_artifacts = _collect_source_signal_artifacts(
                    domains=domains,
                    source_labels=source_labels,
                    platform_mentions=platform_mentions,
                )
                classified_sources = source_signal_artifacts["classified_sources"]
                actionable_platforms = source_signal_artifacts["actionable_platforms"]
                behavior_features = extract_behavior_features(result["text"])
                benchmark_score = (
                    score_against_benchmark(behavior_features, benchmark_features)
                    if benchmark_features
                    else 0.0
                )
                for domain in domains:
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
                all_classified_signals.extend(
                    source_signal_artifacts["unique_platform_signals"]
                )
                benchmark_scores_by_variant.setdefault(prompt_variant, []).append(
                    benchmark_score
                )

                structured_analysis = None
                preprocess_error = None
                try:
                    structured_payload = analyze_answer_record(
                        analyzer=openai_client,
                        question_id=question["question_id"],
                        answer_text=result["text"],
                        prompt_variant=prompt_variant,
                        intent_bucket=question["intent_bucket"],
                        system_prompt=answer_structurer_system,
                        user_template=answer_structurer_user,
                        extracted_urls=urls,
                        extracted_source_labels=source_labels,
                    )
                    structured_analysis = structured_payload_to_dict(structured_payload)
                except Exception as exc:  # pragma: no cover - network path
                    preprocess_error = str(exc)

                answer_record = {
                    "question_id": question["question_id"],
                    "intent_bucket": question["intent_bucket"],
                    "question": question["question"],
                    "rewritten_question": rewritten_question,
                    "prompt_variant": prompt_variant,
                    "text": result["text"],
                    "urls": urls,
                    "domains": domains,
                    "source_labels": source_labels,
                    "platform_mentions": platform_mentions,
                    "classified_sources": classified_sources,
                    "actionable_platforms": actionable_platforms,
                    "structured_analysis": structured_analysis,
                    "preprocess_error": preprocess_error,
                    "behavior_features": asdict(behavior_features),
                    "web_benchmark_score": benchmark_score,
                    "finish_reason": result["finish_reason"],
                    "usage": result["usage"],
                    "error": None,
                }
                _write_json(
                    raw_dir / f"{question['question_id']}-{prompt_variant}.json",
                    result["raw"],
                )
            except Exception as exc:  # pragma: no cover - network path
                answer_record = {
                    "question_id": question["question_id"],
                    "intent_bucket": question["intent_bucket"],
                    "question": question["question"],
                    "rewritten_question": rewritten_question,
                    "prompt_variant": prompt_variant,
                    "text": "",
                    "urls": [],
                    "domains": [],
                    "source_labels": [],
                    "platform_mentions": [],
                    "classified_sources": [],
                    "actionable_platforms": [],
                    "structured_analysis": None,
                    "preprocess_error": None,
                    "behavior_features": None,
                    "web_benchmark_score": 0.0,
                    "finish_reason": None,
                    "usage": None,
                    "error": str(exc),
                }
            answers.append(answer_record)
            current_question_answers.append(answer_record)
            _write_json(run_dir / "answers.json", answers)
            if progress_callback:
                has_error = any(item.get("error") for item in current_question_answers)
                progress_callback(
                    {
                        "question_id": question["question_id"],
                        "question_group": question.get("question_group", "generic"),
                        "intent_bucket": question["intent_bucket"],
                        "question": question["question"],
                        "status": (
                            "error"
                            if has_error
                            and len(current_question_answers)
                            == len(DEFAULT_PROMPT_VARIANTS)
                            else "running"
                        ),
                        "completed_variants": len(current_question_answers),
                        "total_variants": len(DEFAULT_PROMPT_VARIANTS),
                        "answers": [
                            {
                                "prompt_variant": item.get("prompt_variant", ""),
                                "text": item.get("text", ""),
                                "error": item.get("error"),
                            }
                            for item in current_question_answers
                        ],
                    }
                )

        if progress_callback:
            has_error = any(item.get("error") for item in current_question_answers)
            progress_callback(
                {
                    "question_id": question["question_id"],
                    "question_group": question.get("question_group", "generic"),
                    "intent_bucket": question["intent_bucket"],
                    "question": question["question"],
                    "status": "error" if has_error else "completed",
                    "completed_variants": len(current_question_answers),
                    "total_variants": len(DEFAULT_PROMPT_VARIANTS),
                    "answers": [
                        {
                            "prompt_variant": item.get("prompt_variant", ""),
                            "text": item.get("text", ""),
                            "error": item.get("error"),
                        }
                        for item in current_question_answers
                    ],
                }
            )

    variant_summary = summarize_answer_batch(answers)
    top_domains = sorted(domain_counts.items(), key=lambda item: (-item[1], item[0]))
    top_actionable_platforms = summarize_actionable_platforms(all_classified_signals)
    benchmark_summary = {
        variant: round(sum(scores) / len(scores), 4)
        for variant, scores in benchmark_scores_by_variant.items()
        if scores
    }
    platform_analysis = build_platform_analysis(
        answer_records=answers, target_coverage=0.85
    )

    _write_json(run_dir / "answers.json", answers)
    _write_json(
        run_dir / "summary.json",
        {
            "variants": variant_summary,
            "top_domains": top_domains,
            "top_actionable_platforms": top_actionable_platforms,
            "benchmark_summary": benchmark_summary,
            "topic_weights": platform_analysis["topic_weights"],
            "platform_scores": platform_analysis["platform_scores"],
            "golden_set": platform_analysis["golden_set"],
            "baseline_platforms": platform_analysis["baseline_platforms"],
            "niche_opportunities": platform_analysis["niche_opportunities"],
            "niche_golden_set": platform_analysis["niche_golden_set"],
        },
    )

    notes_path = Path("docs") / "findings" / "2026-03-22-doubao-discovery-notes.md"
    _write_markdown(
        notes_path,
        _build_discovery_notes(
            keyword=keyword,
            question_count=len(questions),
            variant_summary=variant_summary,
            top_domains=top_domains,
            top_actionable_platforms=top_actionable_platforms,
            benchmark_summary=benchmark_summary,
        ),
    )

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "question_count": len(questions),
        "answer_count": len(answers),
        "variant_summary": variant_summary,
        "top_domains": top_domains,
        "top_actionable_platforms": top_actionable_platforms,
        "benchmark_summary": benchmark_summary,
        "topic_weights": platform_analysis["topic_weights"],
        "platform_scores": platform_analysis["platform_scores"],
        "golden_set": platform_analysis["golden_set"],
        "baseline_platforms": platform_analysis["baseline_platforms"],
        "niche_opportunities": platform_analysis["niche_opportunities"],
        "niche_golden_set": platform_analysis["niche_golden_set"],
        "notes_path": str(notes_path),
    }
