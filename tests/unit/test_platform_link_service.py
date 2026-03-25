from src.services.platform_link_service import (
    _candidate_urls,
    enrich_platform_rows_with_links,
    platform_primary_url,
)


def test_platform_primary_url_uses_registry_domain() -> None:
    assert platform_primary_url("掘金") == "https://juejin.cn"
    assert platform_primary_url("人人都是产品经理") == "https://woshipm.com"


def test_enrich_platform_rows_with_links_adds_url_and_verification() -> None:
    rows = enrich_platform_rows_with_links(
        [{"platform": "掘金", "niche_opportunity_score": 1.2}],
        verifier=lambda url: {
            "checked_url": url,
            "final_url": url,
            "status_code": 200,
            "status_label": "可访问 (200)",
        },
    )

    assert rows == [
        {
            "platform": "掘金",
            "niche_opportunity_score": 1.2,
            "official_url": "https://juejin.cn",
            "verified_url": "https://juejin.cn",
            "url_status_code": 200,
            "url_verification": "可访问 (200)",
        }
    ]


def test_enrich_platform_rows_with_links_marks_missing_url() -> None:
    rows = enrich_platform_rows_with_links(
        [{"platform": "论坛", "niche_opportunity_score": 0.8}],
        verifier=lambda url: {"status_label": "不应被调用"},
    )

    assert rows == [
        {
            "platform": "论坛",
            "niche_opportunity_score": 0.8,
            "official_url": "",
            "verified_url": "",
            "url_status_code": None,
            "url_verification": "未配置",
        }
    ]


def test_candidate_urls_include_www_and_http_fallbacks() -> None:
    assert _candidate_urls("https://cifnews.com") == [
        "https://cifnews.com",
        "https://www.cifnews.com",
        "http://cifnews.com",
        "http://www.cifnews.com",
    ]


def test_enrich_platform_rows_with_links_uses_verified_url_when_fallback_works() -> (
    None
):
    calls: list[str] = []

    def fake_verifier(url: str) -> dict[str, object]:
        calls.append(url)
        if url == "https://cifnews.com":
            return {
                "checked_url": url,
                "final_url": "",
                "status_code": None,
                "status_label": "校验失败 (timed out)",
            }
        return {
            "checked_url": url,
            "final_url": "https://www.cifnews.com",
            "status_code": 200,
            "status_label": "可访问 (200)",
        }

    rows = enrich_platform_rows_with_links(
        [{"platform": "雨果网", "niche_opportunity_score": 0.6}],
        verifier=fake_verifier,
    )

    assert calls == ["https://cifnews.com", "https://www.cifnews.com"]
    assert rows[0]["official_url"] == "https://cifnews.com"
    assert rows[0]["verified_url"] == "https://www.cifnews.com"
    assert rows[0]["url_verification"] == "可访问 (200)"


def test_enrich_platform_rows_with_links_marks_missing_when_all_candidates_fail() -> (
    None
):
    rows = enrich_platform_rows_with_links(
        [{"platform": "雨果网", "niche_opportunity_score": 0.6}],
        verifier=lambda url: {
            "checked_url": url,
            "final_url": "",
            "status_code": 404,
            "status_label": "未找到",
        },
    )

    assert rows[0]["url_verification"] == "未找到"
