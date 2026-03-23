# pyright: reportMissingImports=false

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.config import load_config
from src.services.draft_service import (
    format_draft_label,
    list_question_drafts,
    load_question_draft,
)
from src.services.distillation_job_service import (
    cancel_job,
    job_state_path,
    load_job_state,
    read_job_log_tail,
    start_distillation_job,
)
from src.ui_helpers import app_css, default_benchmark_path
from src.ui_copy import DISTILL_PAGE
from src.ui_presenters import (
    build_initial_question_progress,
    question_status_glyph,
    question_status_label,
    question_table_height,
)


st.set_page_config(page_title=DISTILL_PAGE["page_title"], layout="wide")
st.markdown(app_css(), unsafe_allow_html=True)

config = load_config()
drafts_dir = config.runs_dir / "question_drafts"
drafts = list_question_drafts(drafts_dir)

st.markdown(f"### {DISTILL_PAGE['heading']}")
st.markdown(
    "<div class='geo-section-card'><strong>页面说明</strong><br/><span class='geo-muted'>第二步基于已经生成好的问题池调用豆包执行蒸馏。这里不会重新生成问题，而是直接对问题池逐条提问、结构化分析并输出评分结果。</span></div>",
    unsafe_allow_html=True,
)


def render_question_progress_list(
    host, progress_rows: dict[str, dict[str, object]]
) -> None:
    ordered_rows = list(progress_rows.values())
    with host.container(height=question_table_height(len(ordered_rows))):
        for item in ordered_rows:
            group_label = (
                "品牌相关" if item.get("question_group") == "brand_specific" else "通用"
            )
            status = str(item.get("status", "pending"))
            answers_value = item.get("answers", [])
            answers = answers_value if isinstance(answers_value, list) else []
            meta_col, text_col, action_col = st.columns([0.7, 6.5, 1.5])
            with meta_col:
                st.markdown(
                    f"<div class='geo-status geo-status-{status}' title='{question_status_label(status)}'>{question_status_glyph(status)}</div>",
                    unsafe_allow_html=True,
                )
            with text_col:
                st.markdown(
                    f"""
                    <div class="geo-question-card">
                      <div class="geo-question-meta">
                        <span class="geo-chip">{item["question_id"]}</span>
                        <span class="geo-chip">{group_label}</span>
                        <span class="geo-chip">{item["intent_bucket"]}</span>
                        <span class="geo-chip">{question_status_label(status)}</span>
                        <span class="geo-chip">{item.get("completed_variants", 0)}/{item.get("total_variants", 0)} 变体</span>
                      </div>
                      <div class="geo-question-title">{item["question"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with action_col:
                with st.popover(DISTILL_PAGE["view_answers"]):
                    st.markdown(f"#### {DISTILL_PAGE['raw_answer_title']}")
                    if not answers:
                        st.info(DISTILL_PAGE["raw_answer_empty"])
                    else:
                        for answer in answers:
                            variant_label = (
                                str(answer.get("prompt_variant", "")) or "未知变体"
                            )
                            text = str(answer.get("text", ""))
                            error = answer.get("error")
                            st.markdown(
                                f"<div class='geo-answer-block'><div class='geo-answer-label'>{variant_label}</div><div class='geo-answer-text'>{text}</div></div>",
                                unsafe_allow_html=True,
                            )
                            if error:
                                st.error(str(error))


if not drafts:
    st.info(DISTILL_PAGE["empty_state"])
else:
    project_root = Path(__file__).resolve().parents[1]
    draft_map = {draft["draft_id"]: draft for draft in drafts}
    selected_draft_id = st.selectbox(
        DISTILL_PAGE["draft_selector"],
        list(draft_map.keys()),
        format_func=format_draft_label,
    )
    if selected_draft_id is None:
        selected_draft_id = next(iter(draft_map))
    selected_draft = draft_map[selected_draft_id]
    loaded_draft = load_question_draft(Path(selected_draft["draft_path"]))
    active_job_id = st.session_state.get("active_distillation_job_id")
    active_job_meta = st.session_state.get("active_distillation_job_meta")
    active_state = None
    if active_job_id:
        state_path = job_state_path(config.runs_dir, active_job_id)
        active_state = load_job_state(state_path)
        if active_state and active_state.get("draft_id") != loaded_draft["draft_id"]:
            active_state = None

    progress_rows = (
        active_state.get("progress_rows", {})
        if active_state
        else build_initial_question_progress(loaded_draft.get("questions", []))
    )
    progress_counter = st.empty()
    progress_placeholder = st.empty()

    top_left, top_right = st.columns([1, 1])
    with top_left:
        if st.button(DISTILL_PAGE["refresh_button"]):
            st.rerun()
    with top_right:
        if active_job_meta and active_state:
            with st.popover(DISTILL_PAGE["job_log_title"]):
                log_text = read_job_log_tail(Path(active_job_meta["log_path"]))
                if log_text:
                    st.code(log_text, language="text")
                else:
                    st.info(DISTILL_PAGE["job_log_empty"])

    if active_state:
        status = active_state.get("status")
        if status == "running":
            st.info(DISTILL_PAGE["job_running"])
            if st.button(DISTILL_PAGE["cancel_button"], type="secondary"):
                state_path = job_state_path(config.runs_dir, str(active_job_id))
                cancel_job(state_path)
                st.rerun()
        elif status == "cancelling":
            st.warning(DISTILL_PAGE["job_cancelling"])
        elif status == "completed":
            st.success(DISTILL_PAGE["job_completed"])
        elif status == "cancelled":
            st.warning(DISTILL_PAGE["job_cancelled"])
        elif status == "error":
            st.error(DISTILL_PAGE["job_error"])
            if active_state.get("error"):
                st.code(str(active_state.get("error")), language="text")

        done_count = sum(
            1
            for row in progress_rows.values()
            if row.get("status") in {"completed", "error"}
        )
        progress_counter.markdown(
            f"<div class='geo-section-card'><strong>{DISTILL_PAGE['progress_title']}</strong><br/><span class='geo-muted'>{DISTILL_PAGE['progress_summary'].format(done=done_count, total=len(progress_rows))}</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown(f"#### {DISTILL_PAGE['draft_preview']}")
    render_question_progress_list(progress_placeholder, progress_rows)

    with st.form("run-distillation"):
        benchmark_file = st.text_input(
            DISTILL_PAGE["benchmark_file_label"],
            value=str(default_benchmark_path()),
            help=DISTILL_PAGE["benchmark_file_help"],
        )
        submitted = st.form_submit_button(DISTILL_PAGE["submit_label"], type="primary")

    if submitted:
        benchmark_path = Path(benchmark_file)
        benchmark_argument = (
            benchmark_path if benchmark_file and benchmark_path.exists() else None
        )

        with st.spinner(DISTILL_PAGE["spinner"]):
            job_meta = start_distillation_job(
                project_root=project_root,
                runs_dir=config.runs_dir,
                draft_path=Path(selected_draft["draft_path"]),
                benchmark_path=benchmark_argument,
            )

        st.session_state["active_distillation_job_id"] = job_meta["job_id"]
        st.session_state["active_distillation_job_meta"] = job_meta
        st.rerun()
