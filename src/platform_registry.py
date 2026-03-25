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
    platform_family: str = ""
    size_tier: str = "niche"
    cost_tier: str = "medium"
    actionability: str = "earned_media"


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
        platform_family="qa_community",
        size_tier="head",
        cost_tier="medium",
        actionability="content_operation",
    ),
    PlatformDefinition(
        "小红书",
        "lifestyle_community",
        "publish_platform",
        True,
        aliases=("小红书",),
        domains=("xiaohongshu.com",),
        platform_family="lifestyle_community",
        size_tier="head",
        cost_tier="medium",
        actionability="content_operation",
    ),
    PlatformDefinition(
        "微信公众号",
        "wechat_media",
        "publish_platform",
        True,
        aliases=("微信公众号", "公众号", "微信公众平台"),
        domains=("mp.weixin.qq.com", "weixin.qq.com"),
        platform_family="wechat_media",
        size_tier="head",
        cost_tier="medium",
        actionability="content_operation",
    ),
    PlatformDefinition(
        "品牌官网",
        "brand_owned",
        "publish_platform",
        True,
        aliases=("品牌官网",),
        domains=(),
        platform_family="owned_media",
        size_tier="owned",
        cost_tier="low",
        actionability="owned_media",
    ),
    PlatformDefinition(
        "36氪",
        "tech_media",
        "publish_platform",
        True,
        aliases=("36氪",),
        domains=("36kr.com",),
        platform_family="tech_media",
        size_tier="head",
        cost_tier="high",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "虎嗅",
        "tech_media",
        "publish_platform",
        True,
        aliases=("虎嗅",),
        domains=("huxiu.com",),
        platform_family="tech_media",
        size_tier="head",
        cost_tier="high",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "IT之家",
        "tech_media",
        "publish_platform",
        True,
        aliases=("IT之家",),
        domains=("ithome.com",),
        platform_family="tech_media",
        size_tier="niche",
        cost_tier="medium",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "界面新闻",
        "news_media",
        "publish_platform",
        True,
        aliases=("界面新闻",),
        domains=("jiemian.com",),
        platform_family="news_media",
        size_tier="head",
        cost_tier="high",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "钛媒体",
        "tech_media",
        "publish_platform",
        True,
        aliases=("钛媒体",),
        domains=("tmtpost.com",),
        platform_family="tech_media",
        size_tier="head",
        cost_tier="high",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "腾讯新闻",
        "news_media",
        "publish_platform",
        True,
        aliases=("腾讯新闻",),
        domains=("xw.qq.com", "news.qq.com"),
        platform_family="news_media",
        size_tier="head",
        cost_tier="high",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "搜狐科技",
        "news_media",
        "publish_platform",
        True,
        aliases=("搜狐科技", "搜狐号"),
        domains=("sohu.com",),
        platform_family="news_media",
        size_tier="head",
        cost_tier="high",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "网易科技",
        "news_media",
        "publish_platform",
        True,
        aliases=("网易科技", "网易号"),
        domains=("163.com",),
        platform_family="news_media",
        size_tier="head",
        cost_tier="high",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "百度百家号",
        "media_platform",
        "publish_platform",
        True,
        aliases=("百家号", "百度百家号"),
        domains=("baijiahao.baidu.com",),
        platform_family="media_platform",
        size_tier="established",
        cost_tier="medium",
        actionability="content_operation",
    ),
    PlatformDefinition(
        "今日头条",
        "media_platform",
        "publish_platform",
        True,
        aliases=("今日头条",),
        domains=("toutiao.com",),
        platform_family="media_platform",
        size_tier="established",
        cost_tier="medium",
        actionability="content_operation",
    ),
    PlatformDefinition(
        "Bilibili",
        "video_community",
        "publish_platform",
        True,
        aliases=("B站", "哔哩哔哩", "Bilibili"),
        domains=("bilibili.com",),
        platform_family="video_community",
        size_tier="established",
        cost_tier="medium",
        actionability="content_operation",
    ),
    PlatformDefinition(
        "CSDN",
        "developer_community",
        "publish_platform",
        True,
        aliases=("CSDN",),
        domains=("csdn.net",),
        platform_family="developer_community",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "SegmentFault",
        "developer_community",
        "publish_platform",
        True,
        aliases=("SegmentFault",),
        domains=("segmentfault.com",),
        platform_family="developer_community",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "少数派",
        "blog_media",
        "publish_platform",
        True,
        aliases=("少数派",),
        domains=("sspai.com",),
        platform_family="blog_media",
        size_tier="niche",
        cost_tier="medium",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "豆瓣",
        "community",
        "publish_platform",
        True,
        aliases=("豆瓣",),
        domains=("douban.com",),
        platform_family="community",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "百度贴吧",
        "forum",
        "publish_platform",
        True,
        aliases=("百度贴吧", "贴吧"),
        domains=("tieba.baidu.com",),
        platform_family="forum",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "V2EX",
        "forum",
        "publish_platform",
        True,
        aliases=("V2EX",),
        domains=("v2ex.com",),
        platform_family="forum",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "站长之家",
        "tech_media",
        "publish_platform",
        True,
        aliases=("站长之家",),
        domains=("chinaz.com", "bbs.chinaz.com"),
        platform_family="tech_media",
        size_tier="niche",
        cost_tier="low",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "A5站长网",
        "tech_media",
        "publish_platform",
        True,
        aliases=("A5站长网",),
        domains=("admin5.com",),
        platform_family="tech_media",
        size_tier="niche",
        cost_tier="low",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "人人都是产品经理",
        "blog_media",
        "publish_platform",
        True,
        aliases=("人人都是产品经理",),
        domains=("woshipm.com",),
        platform_family="blog_media",
        size_tier="niche",
        cost_tier="low",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "数英网",
        "blog_media",
        "publish_platform",
        True,
        aliases=("数英网", "数英DIGITALING"),
        domains=("digitaling.com",),
        platform_family="blog_media",
        size_tier="niche",
        cost_tier="medium",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "鸟哥笔记",
        "blog_media",
        "publish_platform",
        True,
        aliases=("鸟哥笔记",),
        domains=("niaogebiji.com",),
        platform_family="blog_media",
        size_tier="niche",
        cost_tier="low",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "运营派",
        "blog_media",
        "publish_platform",
        True,
        aliases=("运营派",),
        domains=("yunyingpai.com",),
        platform_family="blog_media",
        size_tier="niche",
        cost_tier="low",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "掘金",
        "developer_community",
        "publish_platform",
        True,
        aliases=("掘金",),
        domains=("juejin.cn",),
        platform_family="developer_community",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "博客园",
        "developer_community",
        "publish_platform",
        True,
        aliases=("博客园",),
        domains=("cnblogs.com",),
        platform_family="developer_community",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "本地宝",
        "community",
        "publish_platform",
        True,
        aliases=("本地宝",),
        domains=("bendibao.com",),
        platform_family="community",
        size_tier="niche",
        cost_tier="low",
        actionability="content_operation",
    ),
    PlatformDefinition(
        "19楼",
        "community",
        "publish_platform",
        True,
        aliases=("19楼",),
        domains=("19lou.com",),
        platform_family="community",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "西祠胡同",
        "forum",
        "publish_platform",
        True,
        aliases=("西祠胡同",),
        domains=("xici.net", "xici.com"),
        platform_family="forum",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
    ),
    PlatformDefinition(
        "雨果网",
        "tech_media",
        "publish_platform",
        True,
        aliases=("雨果网",),
        domains=("cifnews.com",),
        platform_family="tech_media",
        size_tier="niche",
        cost_tier="medium",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "白鲸出海",
        "tech_media",
        "publish_platform",
        True,
        aliases=("白鲸出海",),
        domains=("baijingapp.com",),
        platform_family="tech_media",
        size_tier="niche",
        cost_tier="medium",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "InfoQ",
        "tech_media",
        "publish_platform",
        True,
        aliases=("InfoQ",),
        domains=("infoq.cn", "infoq.com"),
        platform_family="tech_media",
        size_tier="niche",
        cost_tier="medium",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "MarTech 中国",
        "tech_media",
        "publish_platform",
        True,
        aliases=("MarTech 中国", "MarTech中国", "MarTech China"),
        domains=("martechchina.com",),
        platform_family="tech_media",
        size_tier="niche",
        cost_tier="medium",
        actionability="earned_media",
    ),
    PlatformDefinition(
        "博客/专栏",
        "blog_media",
        "publish_platform",
        True,
        aliases=("博客", "专栏", "独立博客"),
        domains=(),
        platform_family="blog_media",
        size_tier="niche",
        cost_tier="low",
        actionability="owned_media",
    ),
    PlatformDefinition(
        "论坛",
        "forum",
        "publish_platform",
        True,
        aliases=("论坛", "垂直社区", "行业论坛"),
        domains=(),
        platform_family="forum",
        size_tier="niche",
        cost_tier="low",
        actionability="community_participation",
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


def get_platform_definition(name: str) -> PlatformDefinition | None:
    if not name:
        return None
    return build_platform_index().by_name.get(name)


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
