from __future__ import annotations

import json
from dataclasses import asdict
from sqlite3 import Connection
from typing import Any, Protocol
from uuid import uuid4

from src.platform_registry import classify_source_signal
from src.utils.time_utils import utc_now_iso
from src.utils.url_utils import normalize_domain
from src.utils.validation import (
    StructuredAnswerPayload,
    parse_structured_answer_payload,
)


class AnalyzerProtocol(Protocol):
    def generate_text(
        self,
        *,
        system_prompt: str | None,
        user_prompt: str,
        temperature: float = 0.2,
        max_output_tokens: int = 4000,
    ) -> dict[str, Any]: ...


def _render_user_prompt(
    *,
    user_template: str,
    question_id: str,
    intent_bucket: str,
    prompt_variant: str,
    answer_text: str,
    extracted_urls: list[str],
    extracted_source_labels: list[str],
) -> str:
    return user_template.format(
        question_id=question_id,
        intent_bucket=intent_bucket,
        prompt_variant=prompt_variant,
        answer_text=answer_text,
        citations=json.dumps(extracted_urls, ensure_ascii=False),
        extracted_urls=json.dumps(extracted_urls, ensure_ascii=False),
        source_labels=json.dumps(extracted_source_labels, ensure_ascii=False),
    )


def _insert_source_rows(
    connection: Connection,
    *,
    answer_id: str,
    run_id: str,
    payload: StructuredAnswerPayload,
    extracted_urls: list[str],
    extracted_source_labels: list[str],
) -> None:
    seen: set[tuple[str | None, str | None]] = set()
    created_at = utc_now_iso()
    occurrence_order = 1

    for url in extracted_urls:
        domain = normalize_domain(url)
        key = (domain, url)
        if key in seen:
            continue
        seen.add(key)
        classified = classify_source_signal(domain=domain, source_label=None)
        connection.execute(
            """
            INSERT INTO answer_sources (
                id, answer_id, run_id, domain, source_url, source_label, source_type,
                source_role, normalized_platform, is_actionable_platform,
                occurrence_order, extracted_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                answer_id,
                run_id,
                domain,
                url,
                None,
                "url",
                classified.source_role,
                classified.normalized_platform,
                1 if classified.is_actionable_platform else 0,
                occurrence_order,
                "preprocess_pipeline",
                created_at,
            ),
        )
        occurrence_order += 1

    combined_labels = list(
        dict.fromkeys(extracted_source_labels + payload.source_labels)
    )
    for source_label in combined_labels:
        key = (None, source_label)
        if key in seen:
            continue
        seen.add(key)
        classified = classify_source_signal(domain=None, source_label=source_label)
        connection.execute(
            """
            INSERT INTO answer_sources (
                id, answer_id, run_id, domain, source_url, source_label, source_type,
                source_role, normalized_platform, is_actionable_platform,
                occurrence_order, extracted_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                answer_id,
                run_id,
                None,
                None,
                source_label,
                "label",
                classified.source_role,
                classified.normalized_platform,
                1 if classified.is_actionable_platform else 0,
                occurrence_order,
                "preprocess_pipeline",
                created_at,
            ),
        )
        occurrence_order += 1

    for domain in payload.domains:
        normalized = normalize_domain(domain)
        key = (normalized, None)
        if key in seen:
            continue
        seen.add(key)
        classified = classify_source_signal(domain=normalized, source_label=None)
        connection.execute(
            """
            INSERT INTO answer_sources (
                id, answer_id, run_id, domain, source_url, source_label, source_type,
                source_role, normalized_platform, is_actionable_platform,
                occurrence_order, extracted_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                answer_id,
                run_id,
                normalized,
                None,
                None,
                "domain",
                classified.source_role,
                classified.normalized_platform,
                1 if classified.is_actionable_platform else 0,
                occurrence_order,
                "preprocess_pipeline",
                created_at,
            ),
        )
        occurrence_order += 1


def _insert_topic_rows(
    connection: Connection,
    *,
    answer_id: str,
    run_id: str,
    payload: StructuredAnswerPayload,
) -> None:
    created_at = utc_now_iso()
    for topic_unit in payload.topic_units:
        connection.execute(
            """
            INSERT INTO answer_topic_units (
                id, answer_id, run_id, interpretation_label, brand_grounded,
                source_explicitness_score, provisional_topic_label, claim_text,
                evidence_span, supporting_domains_json, confidence,
                generic_listicle, weak_evidence, self_reference_only, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                answer_id,
                run_id,
                payload.interpretation_label,
                1 if payload.brand_grounded else 0,
                payload.source_explicitness_score,
                topic_unit.topic_label,
                topic_unit.claim,
                topic_unit.evidence_span,
                json.dumps(topic_unit.supporting_domains, ensure_ascii=False),
                topic_unit.confidence,
                1 if payload.noise_flags.generic_listicle else 0,
                1 if payload.noise_flags.weak_evidence else 0,
                1 if payload.noise_flags.self_reference_only else 0,
                created_at,
            ),
        )


def preprocess_answer_record(
    *,
    connection: Connection,
    analyzer: AnalyzerProtocol,
    answer_id: str,
    run_id: str,
    question_id: str,
    answer_text: str,
    prompt_variant: str,
    intent_bucket: str,
    system_prompt: str | None,
    user_template: str,
    extracted_urls: list[str],
    extracted_source_labels: list[str],
) -> StructuredAnswerPayload:
    payload = analyze_answer_record(
        analyzer=analyzer,
        question_id=question_id,
        answer_text=answer_text,
        prompt_variant=prompt_variant,
        intent_bucket=intent_bucket,
        system_prompt=system_prompt,
        user_template=user_template,
        extracted_urls=extracted_urls,
        extracted_source_labels=extracted_source_labels,
    )

    _insert_source_rows(
        connection,
        answer_id=answer_id,
        run_id=run_id,
        payload=payload,
        extracted_urls=extracted_urls,
        extracted_source_labels=extracted_source_labels,
    )
    _insert_topic_rows(
        connection,
        answer_id=answer_id,
        run_id=run_id,
        payload=payload,
    )
    connection.commit()
    return payload


def analyze_answer_record(
    *,
    analyzer: AnalyzerProtocol,
    question_id: str,
    answer_text: str,
    prompt_variant: str,
    intent_bucket: str,
    system_prompt: str | None,
    user_template: str,
    extracted_urls: list[str],
    extracted_source_labels: list[str],
) -> StructuredAnswerPayload:
    user_prompt = _render_user_prompt(
        user_template=user_template,
        question_id=question_id,
        intent_bucket=intent_bucket,
        prompt_variant=prompt_variant,
        answer_text=answer_text,
        extracted_urls=extracted_urls,
        extracted_source_labels=extracted_source_labels,
    )
    last_error: ValueError | None = None
    for attempt in range(2):
        current_user_prompt = user_prompt
        if attempt:
            current_user_prompt = f"{user_prompt}\n\nReturn valid JSON only. Ensure all strings are closed and escaped."
        response = analyzer.generate_text(
            system_prompt=system_prompt,
            user_prompt=current_user_prompt,
            temperature=0.1,
            max_output_tokens=2000,
        )
        try:
            return parse_structured_answer_payload(str(response["text"]))
        except ValueError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def structured_payload_to_dict(payload: StructuredAnswerPayload) -> dict[str, object]:
    return asdict(payload)
