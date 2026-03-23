from __future__ import annotations


def greedy_golden_set(
    *,
    topic_weights: dict[str, float],
    platform_topics: dict[str, set[str]],
    platform_scores: dict[str, float],
    target_coverage: float,
) -> list[dict[str, float | str | list[str]]]:
    total_weight = sum(topic_weights.values()) or 1.0
    covered: set[str] = set()
    remaining = set(platform_topics)
    selected: list[dict[str, float | str | list[str]]] = []

    while remaining:
        best_platform: str | None = None
        best_increment = 0.0
        best_topics: set[str] = set()
        best_score = -1.0

        for platform in sorted(remaining):
            topics = platform_topics.get(platform, set())
            new_topics = topics - covered
            increment = sum(topic_weights.get(topic, 0.0) for topic in new_topics)
            score = platform_scores.get(platform, 0.0)
            if increment > best_increment or (
                increment == best_increment and score > best_score
            ):
                best_platform = platform
                best_increment = increment
                best_topics = new_topics
                best_score = score

        if best_platform is None or best_increment <= 0:
            break

        covered.update(best_topics)
        cumulative = (
            sum(topic_weights.get(topic, 0.0) for topic in covered) / total_weight
        )
        selected.append(
            {
                "platform": best_platform,
                "incremental_coverage": round(best_increment / total_weight, 4),
                "cumulative_coverage": round(cumulative, 4),
                "new_topics": sorted(best_topics),
            }
        )
        remaining.remove(best_platform)

        if cumulative >= target_coverage:
            break

    return selected
