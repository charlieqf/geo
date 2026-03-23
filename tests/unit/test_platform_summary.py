from src.platform_registry import ClassifiedSourceSignal
from src.pipeline.platform_summary import summarize_actionable_platforms


def test_summarize_actionable_platforms_counts_only_actionable_platforms() -> None:
    summary = summarize_actionable_platforms(
        [
            ClassifiedSourceSignal(
                source_role="publish_platform",
                normalized_platform="知乎",
                is_actionable_platform=True,
                platform_type="qa_community",
                matched_by="domain",
            ),
            ClassifiedSourceSignal(
                source_role="publish_platform",
                normalized_platform="知乎",
                is_actionable_platform=True,
                platform_type="qa_community",
                matched_by="label",
            ),
            ClassifiedSourceSignal(
                source_role="infrastructure_site",
                normalized_platform="腾讯云",
                is_actionable_platform=False,
                platform_type="infrastructure",
                matched_by="domain",
            ),
        ]
    )

    assert summary == [("知乎", 2)]
