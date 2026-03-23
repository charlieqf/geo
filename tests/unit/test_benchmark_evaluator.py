from src.pipeline.benchmark_evaluator import (
    extract_behavior_features,
    score_against_benchmark,
)


def test_extract_behavior_features_detects_web_style_signals() -> None:
    text = """
    第一梯队：技术领先型综合服务商
    1. 智推时代
    IT之家
    www.jiasou.cn
    选型建议：先做小规模 POC 测试
    重要提醒：注意平台依赖风险
    GEO（Generative Engine Optimization，生成式引擎优化）
    """

    features = extract_behavior_features(text)

    assert features.correct_geo_interpretation is True
    assert features.has_tier_sections is True
    assert features.has_source_traces is True
    assert features.has_selection_advice is True
    assert features.has_risk_warning is True


def test_score_against_benchmark_rewards_matching_behavior() -> None:
    benchmark = extract_behavior_features(
        """
        第一梯队
        IT之家
        www.jiasou.cn
        选型建议
        重要提醒
        GEO（Generative Engine Optimization）
        """
    )
    candidate = extract_behavior_features(
        """
        第一梯队
        界面新闻
        www.hayepusi.com
        选型建议
        重要提醒
        GEO（Generative Engine Optimization）
        """
    )

    score = score_against_benchmark(candidate, benchmark)

    assert score > 0.7
