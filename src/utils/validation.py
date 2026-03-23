from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


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


@dataclass(frozen=True, slots=True)
class NoiseFlags:
    generic_listicle: bool
    weak_evidence: bool
    self_reference_only: bool


@dataclass(frozen=True, slots=True)
class TopicUnit:
    topic_label: str
    claim: str
    supporting_domains: list[str]
    confidence: float
    evidence_span: str | None


@dataclass(frozen=True, slots=True)
class StructuredAnswerPayload:
    question_id: str
    domains: list[str]
    source_labels: list[str]
    interpretation_label: str
    brand_grounded: bool
    source_explicitness_score: float
    topic_units: list[TopicUnit]
    noise_flags: NoiseFlags


def parse_structured_answer_payload(text: str) -> StructuredAnswerPayload:
    payload = json.loads(_strip_code_fences(text))
    if not isinstance(payload, dict):
        raise ValueError("Structured answer payload must be a JSON object")

    topic_units_raw = payload.get("topic_units")
    if not isinstance(topic_units_raw, list) or not topic_units_raw:
        raise ValueError("topic_units must be a non-empty array")

    topic_units: list[TopicUnit] = []
    for item in topic_units_raw:
        if not isinstance(item, dict):
            raise ValueError("Each topic unit must be an object")
        topic_units.append(
            TopicUnit(
                topic_label=str(item["topic_label"]),
                claim=str(item["claim"]),
                supporting_domains=[
                    str(value) for value in item.get("supporting_domains", [])
                ],
                confidence=float(item["confidence"]),
                evidence_span=(
                    None
                    if item.get("evidence_span") in (None, "")
                    else str(item.get("evidence_span"))
                ),
            )
        )

    noise_flags_raw = payload.get("noise_flags", {})
    if not isinstance(noise_flags_raw, dict):
        raise ValueError("noise_flags must be an object")

    return StructuredAnswerPayload(
        question_id=str(payload["question_id"]),
        domains=[str(value) for value in payload.get("domains", [])],
        source_labels=[str(value) for value in payload.get("source_labels", [])],
        interpretation_label=str(payload.get("interpretation_label", "unknown")),
        brand_grounded=bool(payload.get("brand_grounded", False)),
        source_explicitness_score=float(payload.get("source_explicitness_score", 0.0)),
        topic_units=topic_units,
        noise_flags=NoiseFlags(
            generic_listicle=bool(noise_flags_raw.get("generic_listicle", False)),
            weak_evidence=bool(noise_flags_raw.get("weak_evidence", False)),
            self_reference_only=bool(noise_flags_raw.get("self_reference_only", False)),
        ),
    )
