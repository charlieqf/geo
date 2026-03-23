from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from src.pipeline.discovery_run import parse_question_pool_json
from src.prompt_registry import PromptRegistry
from src.utils.time_utils import utc_now_iso


DEFAULT_QUESTION_COUNT = 20
DEFAULT_BRAND_QUESTION_COUNT = 6


class AnalyzerProtocol(Protocol):
    def generate_text(
        self,
        *,
        system_prompt: str | None,
        user_prompt: str,
        temperature: float = 0.2,
        max_output_tokens: int = 4000,
    ) -> dict[str, object]: ...


def load_question_generation_config(prompts_dir: Path) -> dict[str, Any]:
    config_path = prompts_dir / "question_pool_config.json"
    if not config_path.exists():
        return {
            "default_question_count": DEFAULT_QUESTION_COUNT,
            "brand_question_count": DEFAULT_BRAND_QUESTION_COUNT,
            "generic_intent_buckets": [
                "direct_recommendation",
                "comparison_choice",
                "risk_avoidance",
                "effect_validation",
                "case_reputation",
            ],
            "brand_intent_buckets": ["brand_fit", "brand_evidence", "brand_risk"],
        }
    return json.loads(config_path.read_text(encoding="utf-8"))


def generate_question_draft(
    *,
    keyword: str,
    brand: str,
    analyzer: AnalyzerProtocol,
    prompts_dir: Path,
    storage_dir: Path,
    question_count: int | None = None,
) -> dict[str, Any]:
    registry = PromptRegistry(prompts_dir)
    question_config = load_question_generation_config(prompts_dir)
    default_question_count = int(question_config["default_question_count"])
    resolved_question_count = (
        int(question_count) if question_count is not None else default_question_count
    )
    if resolved_question_count < 1:
        raise ValueError("question_count must be at least 1")
    brand_question_count = int(question_config["brand_question_count"])
    system_prompt = registry.get_prompt("question_pool_system").content.format(
        question_count=resolved_question_count,
        brand_question_count=brand_question_count,
        intent_buckets=", ".join(question_config["generic_intent_buckets"]),
        brand_intent_buckets=", ".join(question_config["brand_intent_buckets"]),
    )
    user_prompt = registry.render(
        "question_pool_user",
        {
            "keywords": keyword,
            "brand": brand or "",
            "brand_instruction": (
                f"品牌：{brand}\n请额外生成 {brand_question_count} 个围绕该品牌、且与关键词强相关的品牌问题。"
                if brand.strip()
                else "品牌为空，请不要生成品牌专属问题。"
            ),
        },
    )
    response = analyzer.generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.2,
        max_output_tokens=3000,
    )
    questions = parse_question_pool_json(str(response["text"]))

    draft_id = f"draft-{keyword.replace(' ', '-').replace('/', '-')}-{utc_now_iso().replace(':', '-')}"
    storage_dir.mkdir(parents=True, exist_ok=True)
    draft_path = storage_dir / f"{draft_id}.json"
    payload = {
        "draft_id": draft_id,
        "keyword": keyword,
        "brand": brand,
        "configured_question_count": resolved_question_count,
        "configured_brand_question_count": brand_question_count,
        "question_count": len(questions),
        "questions": questions,
        "created_at": utc_now_iso(),
    }
    draft_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    payload["draft_path"] = str(draft_path)
    return payload
