# pyright: reportMissingImports=false

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.config import load_config
from src.services.run_service import format_run_label, list_runs, load_run_artifacts
from src.ui_helpers import app_css
from src.ui_copy import PROMPT_VARIANT_LABELS, RESULTS_PAGE
from src.ui_presenters import (
    build_answer_trace_groups,
    present_baseline_platforms,
    present_benchmark_summary,
    present_golden_set,
    present_interpretation_label,
    present_niche_opportunities,
    present_platform_scores,
    present_topic_units,
)


st.set_page_config(page_title=RESULTS_PAGE["page_title"], layout="wide")
st.markdown(app_css(), unsafe_allow_html=True)

config = load_config()
runs = list_runs(config.runs_dir)

st.markdown(f"### {RESULTS_PAGE['heading']}")
if not runs:
    st.info(RESULTS_PAGE["empty_state"])
    st.stop()

run_map = {run["run_id"]: run for run in runs}
selected_run_id = st.selectbox(
    RESULTS_PAGE["run_selector"],
    list(run_map.keys()),
    format_func=format_run_label,
)
if selected_run_id is None:
    selected_run_id = next(iter(run_map))
selected_run = run_map[selected_run_id]
artifacts = load_run_artifacts(Path(selected_run["summary_path"]).parent)
summary = artifacts.get("summary") or {}

platform_scores = summary.get("platform_scores", [])
golden_set = summary.get("golden_set", [])
niche_opportunities = summary.get("niche_opportunities", [])
baseline_platforms = summary.get("baseline_platforms", [])
niche_golden_set = summary.get("niche_golden_set", [])
best_platform = niche_opportunities[0]["platform"] if niche_opportunities else "暂无"
best_score = (
    niche_opportunities[0]["niche_opportunity_score"] if niche_opportunities else 0
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(RESULTS_PAGE["metric_niche_platforms"], len(niche_opportunities))
kpi2.metric(RESULTS_PAGE["metric_baseline_platforms"], len(baseline_platforms))
kpi3.metric(RESULTS_PAGE["metric_best_niche_platform"], best_platform)
kpi4.metric(RESULTS_PAGE["metric_best_niche_score"], best_score)

tab_overview, tab_scores, tab_trace = st.tabs(
    [
        RESULTS_PAGE["tab_overview"],
        RESULTS_PAGE["tab_scores"],
        RESULTS_PAGE["tab_trace"],
    ]
)

with tab_overview:
    left, right = st.columns(2)
    with left:
        st.markdown(f"#### {RESULTS_PAGE['niche_opportunities_title']}")
        if niche_opportunities:
            st.dataframe(
                present_niche_opportunities(niche_opportunities),
                width="stretch",
                hide_index=True,
            )
        else:
            st.info(RESULTS_PAGE["niche_empty"])
    with right:
        st.markdown(f"#### {RESULTS_PAGE['baseline_platforms_title']}")
        st.dataframe(
            present_baseline_platforms(baseline_platforms),
            width="stretch",
            hide_index=True,
        )
    domain_col, benchmark_col = st.columns(2)
    with domain_col:
        st.markdown(f"#### {RESULTS_PAGE['top_domains_title']}")
        st.dataframe(
            [
                {"域名": domain, "出现次数": count}
                for domain, count in selected_run["top_domains"]
            ],
            width="stretch",
            hide_index=True,
        )
    with benchmark_col:
        st.markdown(f"#### {RESULTS_PAGE['benchmark_title']}")
        st.dataframe(
            present_benchmark_summary(selected_run["benchmark_summary"]),
            width="stretch",
            hide_index=True,
        )

with tab_scores:
    score_left, score_right = st.columns([1.5, 1])
    with score_left:
        st.markdown(f"#### {RESULTS_PAGE['platform_scores_title']}")
        st.dataframe(
            present_niche_opportunities(niche_opportunities),
            width="stretch",
            hide_index=True,
        )
    with score_right:
        st.markdown(f"#### {RESULTS_PAGE['golden_set_title']}")
        st.dataframe(
            present_golden_set(niche_golden_set), width="stretch", hide_index=True
        )
        st.markdown(f"#### {RESULTS_PAGE['baseline_scores_title']}")
        st.dataframe(
            present_baseline_platforms(baseline_platforms),
            width="stretch",
            hide_index=True,
        )

with tab_trace:
    questions = artifacts.get("questions") or []
    answers = artifacts.get("answers") or []
    trace_groups = build_answer_trace_groups(questions, answers)
    st.markdown(f"#### {RESULTS_PAGE['answer_trace_title']}")
    st.caption(
        RESULTS_PAGE["trace_summary"].format(
            question_count=len(trace_groups), answer_count=len(answers)
        )
    )
    for group in trace_groups:
        question_group_label = (
            "品牌相关" if group.get("question_group") == "brand_specific" else "通用"
        )
        title = f"{group.get('question_id', '?')} · {group.get('question', '')}"
        with st.expander(title):
            st.caption(
                RESULTS_PAGE["trace_question_meta"].format(
                    group=question_group_label,
                    intent=group.get("intent_bucket", "未知"),
                    variant_count=len(group.get("answers", [])),
                )
            )
            question_answers = group.get("answers", [])
            if not question_answers:
                st.info(RESULTS_PAGE["trace_answer_empty"])
                continue
            tabs = st.tabs(
                [
                    PROMPT_VARIANT_LABELS.get(
                        answer.get("prompt_variant", ""),
                        answer.get("prompt_variant", "未知变体"),
                    )
                    for answer in question_answers
                ]
            )
            for tab, answer in zip(tabs, question_answers):
                with tab:
                    rewritten_question = str(
                        answer.get("rewritten_question", "")
                    ).strip()
                    if rewritten_question:
                        st.caption(
                            RESULTS_PAGE["trace_rewritten"].format(
                                value=rewritten_question
                            )
                        )
                    st.write(answer.get("text", ""))
                    st.caption(
                        RESULTS_PAGE["caption_actionable"].format(
                            value=", ".join(answer.get("actionable_platforms", []))
                            or "暂无"
                        )
                    )
                    st.caption(
                        RESULTS_PAGE["caption_urls"].format(
                            value=", ".join(answer.get("urls", [])) or "暂无"
                        )
                    )
                    st.caption(
                        RESULTS_PAGE["caption_domains"].format(
                            value=", ".join(answer.get("domains", [])) or "暂无"
                        )
                    )
                    structured = answer.get("structured_analysis") or {}
                    if structured:
                        topic_units = structured.get("topic_units") or []
                        st.caption(
                            RESULTS_PAGE["caption_structured"].format(
                                interpretation=present_interpretation_label(
                                    structured.get("interpretation_label", "unknown")
                                ),
                                brand_grounded="是"
                                if structured.get("brand_grounded", False)
                                else "否",
                                score=structured.get("source_explicitness_score", 0.0),
                            )
                        )
                        st.dataframe(
                            present_topic_units(topic_units),
                            width="stretch",
                            hide_index=True,
                        )
                    else:
                        st.info(RESULTS_PAGE["trace_empty"])
