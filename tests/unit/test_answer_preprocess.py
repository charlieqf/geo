import json

import pytest

from src.pipeline.answer_preprocess import analyze_answer_record


class RetryAnalyzer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate_text(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            return {
                "text": '{"question_id":"q1","topic_units":[{"topic_label":"x"}',
                "raw": {},
            }
        return {
            "text": json.dumps(
                {
                    "question_id": "q1",
                    "domains": ["zhihu.com"],
                    "source_labels": ["知乎"],
                    "interpretation_label": "geo_ai_optimization",
                    "brand_grounded": True,
                    "source_explicitness_score": 0.8,
                    "topic_units": [
                        {
                            "topic_label": "高价值平台",
                            "claim": "知乎值得优先布局。",
                            "supporting_domains": ["zhihu.com"],
                            "confidence": 0.9,
                            "evidence_span": "知乎值得优先布局。",
                        }
                    ],
                    "noise_flags": {
                        "generic_listicle": False,
                        "weak_evidence": False,
                        "self_reference_only": False,
                    },
                },
                ensure_ascii=False,
            ),
            "raw": {},
        }


def test_analyze_answer_record_retries_once_when_json_is_invalid() -> None:
    analyzer = RetryAnalyzer()

    payload = analyze_answer_record(
        analyzer=analyzer,
        question_id="q1",
        answer_text="知乎值得优先布局。",
        prompt_variant="web_default",
        intent_bucket="direct_recommendation",
        system_prompt="system prompt",
        user_template=(
            "Question ID: {question_id}\nIntent bucket: {intent_bucket}\n"
            "Prompt variant: {prompt_variant}\nAnswer text: {answer_text}\n"
            "Citations: {citations}\nExtracted urls: {extracted_urls}\n"
            "Extracted source labels: {source_labels}"
        ),
        extracted_urls=[],
        extracted_source_labels=[],
    )

    assert payload.question_id == "q1"
    assert len(analyzer.calls) == 2


def test_analyze_answer_record_raises_after_retry_exhausted() -> None:
    class AlwaysBrokenAnalyzer:
        def __init__(self) -> None:
            self.calls = 0

        def generate_text(self, **kwargs: object) -> dict[str, object]:
            self.calls += 1
            return {"text": "{not json", "raw": {}}

    analyzer = AlwaysBrokenAnalyzer()

    with pytest.raises(ValueError):
        analyze_answer_record(
            analyzer=analyzer,
            question_id="q1",
            answer_text="知乎值得优先布局。",
            prompt_variant="web_default",
            intent_bucket="direct_recommendation",
            system_prompt="system prompt",
            user_template=(
                "Question ID: {question_id}\nIntent bucket: {intent_bucket}\n"
                "Prompt variant: {prompt_variant}\nAnswer text: {answer_text}\n"
                "Citations: {citations}\nExtracted urls: {extracted_urls}\n"
                "Extracted source labels: {source_labels}"
            ),
            extracted_urls=[],
            extracted_source_labels=[],
        )

    assert analyzer.calls == 2
