from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re

from src.utils.url_utils import normalize_domain


@dataclass(frozen=True, slots=True)
class PlatformDefinition:
    display_name: str
    platform_type: str
    source_role: str
    is_actionable_platform: bool
    aliases: tuple[str, ...] = ()
    domains: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PlatformIndex:
    by_name: dict[str, PlatformDefinition]
    by_domain: dict[str, PlatformDefinition]


@dataclass(frozen=True, slots=True)
class ClassifiedSourceSignal:
    source_role: str
    normalized_platform: str | None
    is_actionable_platform: bool
    platform_type: str
    matched_by: str


FUZZY_LABEL_EXCLUDE_ALIASES = {
    "官网",
    "专题页",
    "案例页",
    "公众号",
    "微信公众平台",
    "搜狐号",
    "网易号",
    "博客",
    "专栏",
    "独立博客",
    "论坛",
    "垂直社区",
    "行业论坛",
    "贴吧",
}


PUBLISH_PLATFORM_DEFINITIONS: tuple[PlatformDefinition, ...] = (
    PlatformDefinition(
        "知乎",
        "qa_community",
        "publish_platform",
        True,
        aliases=("知乎",),
        domains=("zhihu.com",),
    ),
    PlatformDefinition(
        "小红书",
        "lifestyle_community",
        "publish_platform",
        True,
        aliases=("小红书",),
        domains=("xiaohongshu.com",),
    ),
    PlatformDefinition(
        "微信公众号",
        "wechat_media",
        "publish_platform",
        True,
        aliases=("微信公众号", "公众号", "微信公众平台"),
        domains=("mp.weixin.qq.com", "weixin.qq.com"),
    ),
    PlatformDefinition(
        "品牌官网",
        "brand_owned",
        "publish_platform",
        True,
        aliases=("品牌官网",),
        domains=(),
    ),
    PlatformDefinition(
        "36氪",
        "tech_media",
        "publish_platform",
        True,
        aliases=("36氪",),
        domains=("36kr.com",),
    ),
    PlatformDefinition(
        "虎嗅",
        "tech_media",
        "publish_platform",
        True,
        aliases=("虎嗅",),
        domains=("huxiu.com",),
    ),
    PlatformDefinition(
        "IT之家",
        "tech_media",
        "publish_platform",
        True,
        aliases=("IT之家",),
        domains=("ithome.com",),
    ),
    PlatformDefinition(
        "界面新闻",
        "news_media",
        "publish_platform",
        True,
        aliases=("界面新闻",),
        domains=("jiemian.com",),
    ),
    PlatformDefinition(
        "钛媒体",
        "tech_media",
        "publish_platform",
        True,
        aliases=("钛媒体",),
        domains=("tmtpost.com",),
    ),
    PlatformDefinition(
        "腾讯新闻",
        "news_media",
        "publish_platform",
        True,
        aliases=("腾讯新闻",),
        domains=("xw.qq.com", "news.qq.com"),
    ),
    PlatformDefinition(
        "搜狐科技",
        "news_media",
        "publish_platform",
        True,
        aliases=("搜狐科技", "搜狐号"),
        domains=("sohu.com",),
    ),
    PlatformDefinition(
        "网易科技",
        "news_media",
        "publish_platform",
        True,
        aliases=("网易科技", "网易号"),
        domains=("163.com",),
    ),
    PlatformDefinition(
        "百度百家号",
        "media_platform",
        "publish_platform",
        True,
        aliases=("百家号", "百度百家号"),
        domains=("baijiahao.baidu.com",),
    ),
    PlatformDefinition(
        "今日头条",
        "media_platform",
        "publish_platform",
        True,
        aliases=("今日头条",),
        domains=("toutiao.com",),
    ),
    PlatformDefinition(
        "Bilibili",
        "video_community",
        "publish_platform",
        True,
        aliases=("B站", "哔哩哔哩", "Bilibili"),
        domains=("bilibili.com",),
    ),
    PlatformDefinition(
        "CSDN",
        "developer_community",
        "publish_platform",
        True,
        aliases=("CSDN",),
        domains=("csdn.net",),
    ),
    PlatformDefinition(
        "SegmentFault",
        "developer_community",
        "publish_platform",
        True,
        aliases=("SegmentFault",),
        domains=("segmentfault.com",),
    ),
    PlatformDefinition(
        "少数派",
        "blog_media",
        "publish_platform",
        True,
        aliases=("少数派",),
        domains=("sspai.com",),
    ),
    PlatformDefinition(
        "豆瓣",
        "community",
        "publish_platform",
        True,
        aliases=("豆瓣",),
        domains=("douban.com",),
    ),
    PlatformDefinition(
        "百度贴吧",
        "forum",
        "publish_platform",
        True,
        aliases=("百度贴吧", "贴吧"),
        domains=("tieba.baidu.com",),
    ),
    PlatformDefinition(
        "V2EX",
        "forum",
        "publish_platform",
        True,
        aliases=("V2EX",),
        domains=("v2ex.com",),
    ),
    PlatformDefinition(
        "博客/专栏",
        "blog_media",
        "publish_platform",
        True,
        aliases=("博客", "专栏", "独立博客"),
        domains=(),
    ),
    PlatformDefinition(
        "论坛",
        "forum",
        "publish_platform",
        True,
        aliases=("论坛", "垂直社区", "行业论坛"),
        domains=(),
    ),
)

NON_ACTIONABLE_DEFINITIONS: tuple[PlatformDefinition, ...] = (
    PlatformDefinition(
        "阿里云",
        "infrastructure",
        "infrastructure_site",
        False,
        aliases=("阿里云",),
        domains=("aliyun.com", "alibabacloud.com"),
    ),
    PlatformDefinition(
        "百度智能云",
        "infrastructure",
        "infrastructure_site",
        False,
        aliases=("百度智能云",),
        domains=("cloud.baidu.com",),
    ),
    PlatformDefinition(
        "腾讯云",
        "infrastructure",
        "infrastructure_site",
        False,
        aliases=("腾讯云",),
        domains=("cloud.tencent.com", "tencentcloud.com"),
    ),
    PlatformDefinition(
        "华为云",
        "infrastructure",
        "infrastructure_site",
        False,
        aliases=("华为云",),
        domains=("huaweicloud.com",),
    ),
    PlatformDefinition(
        "讯飞开放平台",
        "infrastructure",
        "infrastructure_site",
        False,
        aliases=("讯飞开放平台",),
        domains=("iflytek.com",),
    ),
)


def _all_platforms() -> tuple[PlatformDefinition, ...]:
    return PUBLISH_PLATFORM_DEFINITIONS + NON_ACTIONABLE_DEFINITIONS


@lru_cache(maxsize=1)
def build_platform_index() -> PlatformIndex:
    by_name: dict[str, PlatformDefinition] = {}
    by_domain: dict[str, PlatformDefinition] = {}
    for definition in _all_platforms():
        by_name[definition.display_name] = definition
        for alias in definition.aliases:
            by_name[alias] = definition
        for domain in definition.domains:
            by_domain[domain] = definition
    return PlatformIndex(by_name=by_name, by_domain=by_domain)


def _match_by_domain(domain: str | None) -> PlatformDefinition | None:
    if not domain:
        return None
    normalized = normalize_domain(domain)
    if not normalized:
        return None

    index = build_platform_index()
    best_match: PlatformDefinition | None = None
    best_length = -1
    for candidate_domain, definition in index.by_domain.items():
        if normalized == candidate_domain or normalized.endswith(
            f".{candidate_domain}"
        ):
            if len(candidate_domain) > best_length:
                best_length = len(candidate_domain)
                best_match = definition
    return best_match


def _match_by_label(source_label: str | None) -> PlatformDefinition | None:
    if not source_label:
        return None
    cleaned = source_label.strip()
    if not cleaned:
        return None
    index = build_platform_index()
    exact_match = index.by_name.get(cleaned)
    if exact_match:
        return exact_match

    aliases = sorted(index.by_name.items(), key=lambda item: len(item[0]), reverse=True)
    for alias, definition in aliases:
        if not alias or alias in FUZZY_LABEL_EXCLUDE_ALIASES or len(alias) < 3:
            continue
        if alias in cleaned:
            return definition
    return None


def classify_source_signal(
    *, domain: str | None, source_label: str | None
) -> ClassifiedSourceSignal:
    matched_label = _match_by_label(source_label)
    if matched_label:
        return ClassifiedSourceSignal(
            source_role=matched_label.source_role,
            normalized_platform=matched_label.display_name,
            is_actionable_platform=matched_label.is_actionable_platform,
            platform_type=matched_label.platform_type,
            matched_by="label",
        )

    matched_domain = _match_by_domain(domain)
    if matched_domain:
        return ClassifiedSourceSignal(
            source_role=matched_domain.source_role,
            normalized_platform=matched_domain.display_name,
            is_actionable_platform=matched_domain.is_actionable_platform,
            platform_type=matched_domain.platform_type,
            matched_by="domain",
        )

    return ClassifiedSourceSignal(
        source_role="unknown",
        normalized_platform=None,
        is_actionable_platform=False,
        platform_type="unknown",
        matched_by="none",
    )


def extract_platform_mentions(text: str) -> list[str]:
    seen: set[str] = set()
    mentions: list[str] = []
    for alias, definition in build_platform_index().by_name.items():
        if not alias:
            continue
        if re.search(re.escape(alias), text, flags=re.IGNORECASE):
            if definition.display_name not in seen:
                seen.add(definition.display_name)
                mentions.append(definition.display_name)
    return sorted(mentions)
