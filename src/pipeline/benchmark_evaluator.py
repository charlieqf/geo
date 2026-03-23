from __future__ import annotations

from dataclasses import dataclass

from src.utils.url_utils import extract_source_labels


@dataclass(frozen=True, slots=True)
class BehaviorFeatures:
    correct_geo_interpretation: bool
    wrong_geo_interpretation: bool
    has_tier_sections: bool
    has_source_traces: bool
    has_selection_advice: bool
    has_risk_warning: bool
    vendor_line_count: int


def extract_behavior_features(text: str) -> BehaviorFeatures:
    lowered = text.lower()
    correct_geo_interpretation = (
        "generative engine optimization" in lowered
        or "生成式引擎优化" in text
        or "ai引用优化" in text
        or "ai 搜索" in text
    )
    wrong_geo_interpretation = (
        any(
            token in text
            for token in (
                "地理编码",
                "地理围栏",
                "地图服务",
                "earth observation",
                "gis",
            )
        )
        and not correct_geo_interpretation
    )
    has_tier_sections = any(
        token in text
        for token in ("第一梯队", "第二梯队", "垂直领域", "预算有限", "服务商盘点")
    )
    has_source_traces = bool(extract_source_labels(text))
    has_selection_advice = any(
        token in text for token in ("选型建议", "适用客户", "推荐服务商", "POC")
    )
    has_risk_warning = any(
        token in text for token in ("重要提醒", "风险", "合规", "平台依赖")
    )
    vendor_line_count = sum(
        1
        for line in text.splitlines()
        if line.strip().startswith(tuple(str(index) + "." for index in range(1, 10)))
    )
    return BehaviorFeatures(
        correct_geo_interpretation=correct_geo_interpretation,
        wrong_geo_interpretation=wrong_geo_interpretation,
        has_tier_sections=has_tier_sections,
        has_source_traces=has_source_traces,
        has_selection_advice=has_selection_advice,
        has_risk_warning=has_risk_warning,
        vendor_line_count=vendor_line_count,
    )


def score_against_benchmark(
    candidate: BehaviorFeatures, benchmark: BehaviorFeatures
) -> float:
    weights = {
        "correct_geo_interpretation": 0.3,
        "has_tier_sections": 0.2,
        "has_source_traces": 0.2,
        "has_selection_advice": 0.15,
        "has_risk_warning": 0.15,
    }
    score = 0.0
    for field_name, weight in weights.items():
        if getattr(benchmark, field_name) and getattr(candidate, field_name):
            score += weight

    if benchmark.wrong_geo_interpretation and not candidate.wrong_geo_interpretation:
        score += 0.0
    elif candidate.wrong_geo_interpretation:
        score *= 0.5

    return round(min(score, 1.0), 4)
