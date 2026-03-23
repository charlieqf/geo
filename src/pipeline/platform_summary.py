from __future__ import annotations

from collections import Counter

from src.platform_registry import ClassifiedSourceSignal


def summarize_actionable_platforms(
    signals: list[ClassifiedSourceSignal],
) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for signal in signals:
        if signal.is_actionable_platform and signal.normalized_platform:
            counter[signal.normalized_platform] += 1
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))
