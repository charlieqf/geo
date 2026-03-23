from __future__ import annotations

import re
from urllib.parse import urlparse


URL_PATTERN = re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&*+,;=%-]+")
DOMAIN_PATTERN = re.compile(r"\b(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
MEDIA_LABEL_PATTERN = re.compile(
    r"^[A-Za-z0-9\u4e00-\u9fff·()（）-]{2,20}(新闻|日报|时报|晚报|周刊|传媒|财经|观察|之家|网)?$"
)
SOURCE_ITEM_PATTERN = re.compile(r"(?:^|[；;\n]\s*)(?:\d+[.、]\s*)([^；;\n]+)")
PUBLISH_LABEL_HINTS = (
    "新闻",
    "传媒",
    "财经",
    "观察",
    "之家",
    "界面",
    "中华网",
    "IT",
    "网",
    "知乎",
    "小红书",
    "百家号",
    "头条",
    "虎嗅",
    "36氪",
    "钛媒体",
    "豆瓣",
    "贴吧",
    "V2EX",
    "公众号",
)
SOURCE_SECTION_STOP_MARKERS = (
    "潜在高价值信息平台",
    "选型建议",
    "风险提醒",
    "归纳判断",
    "服务商盘点",
    "来自公开来源的信息",
)
SOURCE_LABEL_HINTS = (
    "《",
    "》",
    "官网",
    "公众号",
    "白皮书",
    "报告",
    "指引",
    "调查",
    "研究",
    "盘点",
    "专题",
)


def _clean_source_candidate(text: str) -> str:
    candidate = text.strip().strip("-•* ")
    candidate = candidate.strip(";；,，。:：")
    return candidate.strip()


def _looks_like_source_label(candidate: str) -> bool:
    if not candidate:
        return False
    if DOMAIN_PATTERN.fullmatch(candidate):
        return True
    return any(token in candidate for token in SOURCE_LABEL_HINTS)


def _extract_inline_source_labels(text: str) -> list[str]:
    if "信息来源" not in text:
        return []

    source_zone = text.split("信息来源", maxsplit=1)[1].lstrip("：: \n")
    stop_indexes = [
        source_zone.find(marker)
        for marker in SOURCE_SECTION_STOP_MARKERS
        if source_zone.find(marker) != -1
    ]
    if stop_indexes:
        source_zone = source_zone[: min(stop_indexes)]

    labels: list[str] = []
    seen: set[str] = set()
    for match in SOURCE_ITEM_PATTERN.findall(source_zone):
        candidate = _clean_source_candidate(match)
        if not _looks_like_source_label(candidate) or candidate in seen:
            continue
        seen.add(candidate)
        labels.append(candidate)
    return labels


def extract_urls(text: str) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for match in URL_PATTERN.findall(text):
        cleaned = match.rstrip(".,;:!?)]}>'\"，。；：！？、】【）》」』")
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            urls.append(cleaned)
    return urls


def normalize_domain(value: str) -> str | None:
    candidate = value.strip()
    if not candidate:
        return None
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    domain = parsed.netloc or parsed.path
    domain = domain.lower().split(":", maxsplit=1)[0]
    if domain.startswith("www."):
        domain = domain[4:]
    return domain or None


def extract_domains(text: str) -> list[str]:
    seen: set[str] = set()
    domains: list[str] = []
    extracted_urls = extract_urls(text)

    for url in extracted_urls:
        normalized = normalize_domain(url)
        if normalized and normalized not in seen:
            seen.add(normalized)
            domains.append(normalized)

    residual_text = text
    for url in extracted_urls:
        residual_text = residual_text.replace(url, " ")

    for token in DOMAIN_PATTERN.findall(residual_text):
        normalized = normalize_domain(token)
        if normalized and normalized not in seen:
            seen.add(normalized)
            domains.append(normalized)

    return domains


def extract_source_labels(text: str) -> list[str]:
    seen: set[str] = set()
    labels: list[str] = []
    for candidate in _extract_inline_source_labels(text):
        if candidate not in seen:
            seen.add(candidate)
            labels.append(candidate)
    for raw_line in text.splitlines():
        line = raw_line.strip().strip("-•* ")
        if not line:
            continue
        if DOMAIN_PATTERN.fullmatch(line):
            if line not in seen:
                seen.add(line)
                labels.append(line)
            continue
        if any(char.isdigit() for char in line[:2]):
            continue
        if MEDIA_LABEL_PATTERN.fullmatch(line) and any(
            token in line for token in PUBLISH_LABEL_HINTS
        ):
            if line not in seen:
                seen.add(line)
                labels.append(line)
    return labels
