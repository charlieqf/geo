from src.platform_registry import (
    build_platform_index,
    classify_source_signal,
    extract_platform_mentions,
    get_platform_definition,
)


def test_platform_registry_contains_core_actionable_platforms() -> None:
    index = build_platform_index()

    assert "知乎" in index.by_name
    assert "小红书" in index.by_name
    assert "IT之家" in index.by_name
    assert "微信公众号" in index.by_name


def test_classify_source_signal_maps_publish_platforms_and_infrastructure() -> None:
    zhihu = classify_source_signal(domain="zhihu.com", source_label=None)
    tencent_cloud = classify_source_signal(
        domain="cloud.tencent.com", source_label=None
    )
    ithome = classify_source_signal(domain=None, source_label="IT之家")

    assert zhihu.source_role == "publish_platform"
    assert zhihu.normalized_platform == "知乎"
    assert zhihu.is_actionable_platform is True

    assert ithome.source_role == "publish_platform"
    assert ithome.normalized_platform == "IT之家"
    assert ithome.is_actionable_platform is True

    assert tencent_cloud.source_role == "infrastructure_site"
    assert tencent_cloud.is_actionable_platform is False


def test_classify_source_signal_keeps_unknown_unknown() -> None:
    result = classify_source_signal(domain="example.org", source_label=None)

    assert result.source_role == "unknown"
    assert result.normalized_platform is None
    assert result.is_actionable_platform is False


def test_classify_source_signal_matches_compound_media_labels() -> None:
    kr = classify_source_signal(
        domain=None,
        source_label="36氪《2024生成式AI To B应用行业研究》",
    )
    tmt = classify_source_signal(
        domain=None,
        source_label="钛媒体2024年3月报道《GEO行业观察》",
    )

    assert kr.normalized_platform == "36氪"
    assert kr.matched_by == "label"
    assert tmt.normalized_platform == "钛媒体"
    assert tmt.matched_by == "label"


def test_extract_platform_mentions_finds_actionable_platforms_in_prose() -> None:
    mentions = extract_platform_mentions(
        "潜在高价值信息平台包括知乎、小红书、IT之家和微信公众号，但不要把阿里云算进去。"
    )

    assert mentions == ["IT之家", "小红书", "微信公众号", "知乎", "阿里云"]


def test_extract_platform_mentions_skips_ambiguous_official_site_aliases() -> None:
    mentions = extract_platform_mentions("可参考新榜官网和珍岛集团官网的服务介绍页。")

    assert "品牌官网" not in mentions


def test_platform_metadata_distinguishes_head_and_niche_platforms() -> None:
    kr = get_platform_definition("36氪")
    ithome = get_platform_definition("IT之家")

    assert kr is not None
    assert ithome is not None
    assert kr.size_tier == "head"
    assert kr.cost_tier == "high"
    assert ithome.size_tier == "niche"
    assert ithome.actionability == "earned_media"
