from src.pipeline.golden_set import greedy_golden_set


def test_greedy_golden_set_prefers_highest_marginal_coverage() -> None:
    topic_weights = {
        "A": 0.45,
        "B": 0.35,
        "C": 0.20,
    }
    platform_topics = {
        "知乎": {"A", "B"},
        "小红书": {"C"},
        "IT之家": {"B"},
    }
    platform_scores = {
        "知乎": 0.85,
        "小红书": 0.71,
        "IT之家": 0.54,
    }

    selected = greedy_golden_set(
        topic_weights=topic_weights,
        platform_topics=platform_topics,
        platform_scores=platform_scores,
        target_coverage=0.81,
    )

    assert [item["platform"] for item in selected] == ["知乎", "小红书"]
    assert selected[-1]["cumulative_coverage"] == 1.0
