from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from src.platform_registry import get_platform_definition


def platform_primary_url(platform_name: str) -> str | None:
    definition = get_platform_definition(platform_name)
    if not definition or not definition.domains:
        return None
    return f"https://{definition.domains[0]}"


def _candidate_urls(url: str) -> list[str]:
    parsed = urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        return [url]

    netlocs = [parsed.netloc]
    if not parsed.netloc.startswith("www."):
        netlocs.append(f"www.{parsed.netloc}")

    candidates: list[str] = []
    for scheme in (parsed.scheme, "http" if parsed.scheme == "https" else "https"):
        for netloc in netlocs:
            candidate = urlunsplit(
                (scheme, netloc, parsed.path, parsed.query, parsed.fragment)
            )
            if candidate not in candidates:
                candidates.append(candidate)
    return candidates


@lru_cache(maxsize=256)
def verify_platform_url(url: str, timeout: float = 5.0) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            status_code = getattr(response, "status", 200)
            final_url = response.geturl()
            return {
                "checked_url": url,
                "final_url": final_url,
                "status_code": status_code,
                "status_label": f"可访问 ({status_code})",
            }
    except HTTPError as exc:
        return {
            "checked_url": url,
            "final_url": url,
            "status_code": exc.code,
            "status_label": f"失败 ({exc.code})",
        }
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        return {
            "checked_url": url,
            "final_url": "",
            "status_code": None,
            "status_label": f"失败 ({reason})",
        }


def enrich_platform_rows_with_links(
    rows: list[dict[str, Any]],
    verifier: Callable[[str], dict[str, Any]] = verify_platform_url,
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for row in rows:
        platform_name = str(row.get("platform", ""))
        official_url = platform_primary_url(platform_name)
        next_row = dict(row)
        if not official_url:
            next_row.update(
                {
                    "official_url": "",
                    "verified_url": "",
                    "url_status_code": None,
                    "url_verification": "未配置",
                }
            )
            enriched.append(next_row)
            continue

        verification: dict[str, Any] | None = None
        last_failure: dict[str, Any] | None = None
        for candidate_url in _candidate_urls(official_url):
            current = verifier(candidate_url)
            status_code = current.get("status_code")
            if status_code is not None and int(status_code) < 400:
                verification = current
                break
            last_failure = current

        if verification is None:
            verification = last_failure or {
                "checked_url": official_url,
                "final_url": "",
                "status_code": None,
                "status_label": "未找到",
            }

        status_code = verification.get("status_code")
        status_label = verification.get("status_label", "未校验")
        if status_code == 404:
            status_label = "未找到"
        next_row.update(
            {
                "official_url": official_url,
                "verified_url": str(verification.get("final_url") or official_url),
                "url_status_code": status_code,
                "url_verification": status_label,
            }
        )
        enriched.append(next_row)
    return enriched
