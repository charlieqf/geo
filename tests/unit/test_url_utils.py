from src.utils.url_utils import (
    extract_domains,
    extract_source_labels,
    extract_urls,
    normalize_domain,
)


def test_extract_urls_returns_unique_urls_in_order() -> None:
    text = "参考 https://www.zhihu.com/question/1 以及 https://www.zhihu.com/question/1 和 http://example.com/path"

    assert extract_urls(text) == [
        "https://www.zhihu.com/question/1",
        "http://example.com/path",
    ]


def test_normalize_domain_handles_urls_with_scheme() -> None:
    assert normalize_domain("https://www.zhihu.com/question/1") == "zhihu.com"


def test_normalize_domain_handles_bare_domains() -> None:
    assert normalize_domain("www.xiaohongshu.com") == "xiaohongshu.com"


def test_extract_source_labels_handles_media_names_and_domains() -> None:
    text = "IT之家\n界面新闻\nwww.jiasou.cn\nnews.bjd.com.cn"

    assert extract_source_labels(text) == [
        "IT之家",
        "界面新闻",
        "www.jiasou.cn",
        "news.bjd.com.cn",
    ]


def test_extract_urls_stops_before_chinese_punctuation_and_following_text() -> None:
    text = (
        "白鲸出海（https://www.baijingapp.com）、跨境知道；"
        "刀法网（https://www.daofa.net）、品牌星球（https://www.brandstar.com.cn）。"
    )

    assert extract_urls(text) == [
        "https://www.baijingapp.com",
        "https://www.daofa.net",
        "https://www.brandstar.com.cn",
    ]


def test_extract_source_labels_handles_inline_numbered_sources() -> None:
    text = (
        "信息来源：1. 中国广告协会《2024生成式营销服务规范指引》；"
        "2. 36氪《2024年GEO行业调研白皮书》；"
        "3. 钛媒体《GEO服务乱象调查：8成服务商无法提供可量化效果证明》"
    )

    assert extract_source_labels(text) == [
        "中国广告协会《2024生成式营销服务规范指引》",
        "36氪《2024年GEO行业调研白皮书》",
        "钛媒体《GEO服务乱象调查：8成服务商无法提供可量化效果证明》",
    ]


def test_extract_domains_ignores_url_path_filenames() -> None:
    text = "清博智能GEO相关服务公开说明：https://www.gsdata.cn/product/custom.html"

    assert extract_domains(text) == ["gsdata.cn"]


def test_extract_domains_ignores_standalone_html_path_fragments() -> None:
    text = (
        "抓到的脏路径包括 forum-123-1.html 和 weight.html，"
        "但合法来源只有 https://www.gsdata.cn/product/custom.html 和 bendibao.com"
    )

    assert extract_domains(text) == ["gsdata.cn", "bendibao.com"]
