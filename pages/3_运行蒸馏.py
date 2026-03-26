# pyright: reportMissingImports=false

from __future__ import annotations

from html import escape
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
    latest_job_meta_for_draft,
    load_job_state,
    read_job_log_tail,
    start_distillation_job,
)
from src.ui_helpers import app_css
from src.ui_copy import DISTILL_PAGE, PROMPT_VARIANT_EXPLANATIONS, PROMPT_VARIANT_LABELS
from src.ui_presenters import (
    build_initial_question_progress,
    distillation_preview_height,
    question_status_glyph,
    question_status_label,
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
    with host.container(height=distillation_preview_height(len(ordered_rows))):
        for item in ordered_rows:
            group_label = (
                "品牌相关" if item.get("question_group") == "brand_specific" else "通用"
            )
            status = str(item.get("status", "pending"))
            answers_value = item.get("answers", [])
            answers = answers_value if isinstance(answers_value, list) else []
            meta_col, text_col, action_col = st.columns([1, 8, 2])
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
                if st.button(
                    DISTILL_PAGE["view_answers"],
                    key=f"view-answer-{item['question_id']}",
                    use_container_width=True,
                ):
                    st.session_state["distillation_preview_question_id"] = item[
                        "question_id"
                    ]
                    st.rerun()


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

    latest_job_meta = latest_job_meta_for_draft(
        config.runs_dir, loaded_draft["draft_id"]
    )
    latest_state = None
    if latest_job_meta:
        latest_state = load_job_state(Path(latest_job_meta["state_path"]))

    display_job_meta = active_job_meta if active_state else latest_job_meta
    display_state = active_state or latest_state

    progress_rows = (
        display_state.get("progress_rows", {})
        if display_state
        else build_initial_question_progress(loaded_draft.get("questions", []))
    )
    progress_placeholder = st.empty()
    done_count = sum(
        1
        for row in progress_rows.values()
        if row.get("status") in {"completed", "error"}
    )

    st.markdown(f"#### {DISTILL_PAGE['draft_preview']}")
    render_question_progress_list(progress_placeholder, progress_rows)

    status_col, control_col = st.columns([1.25, 0.9], gap="large")
    with status_col:
        st.markdown(f"#### {DISTILL_PAGE['status_panel_title']}")
        st.markdown(
            f"<div class='geo-section-card'><strong>{DISTILL_PAGE['progress_title']}</strong><br/><span class='geo-muted'>{DISTILL_PAGE['progress_summary'].format(done=done_count, total=len(progress_rows))}</span></div>",
            unsafe_allow_html=True,
        )
        if display_state:
            status = display_state.get("status")
            if status == "running":
                st.info(DISTILL_PAGE["job_running"])
            elif status == "cancelling":
                st.warning(DISTILL_PAGE["job_cancelling"])
            elif status == "completed":
                st.success(DISTILL_PAGE["job_completed"])
            elif status == "cancelled":
                st.warning(DISTILL_PAGE["job_cancelled"])
            elif status == "error":
                st.error(DISTILL_PAGE["job_error"])
                if display_state.get("error"):
                    st.code(str(display_state.get("error")), language="text")
        else:
            st.info(DISTILL_PAGE["ready_hint"])

    with control_col:
        st.markdown(f"#### {DISTILL_PAGE['control_panel_title']}")
        action_left, action_right = st.columns(2)
        with action_left:
            start_requested = st.button(
                DISTILL_PAGE["submit_label"],
                type="primary",
                use_container_width=True,
                disabled=bool(
                    active_state
                    and active_state.get("status") in {"running", "cancelling"}
                ),
            )
        with action_right:
            refresh_requested = st.button(
                DISTILL_PAGE["refresh_button"],
                use_container_width=True,
            )

        if refresh_requested:
            st.rerun()

        if (
            display_job_meta
            and display_state
            and display_state.get("status") == "running"
        ):
            if st.button(
                DISTILL_PAGE["cancel_button"],
                type="secondary",
                use_container_width=True,
            ):
                state_path = job_state_path(config.runs_dir, str(active_job_id))
                cancel_job(state_path)
                st.rerun()

        with st.expander(DISTILL_PAGE["job_log_title"], expanded=False):
            if display_job_meta:
                log_text = read_job_log_tail(Path(display_job_meta["log_path"]))
                if log_text:
                    st.code(log_text, language="text")
                else:
                    st.info(DISTILL_PAGE["job_log_empty"])
            else:
                st.info(DISTILL_PAGE["job_log_empty"])

    selected_question_id = st.session_state.get("distillation_preview_question_id")
    if selected_question_id not in progress_rows:
        selected_question_id = next(iter(progress_rows), None)
        st.session_state["distillation_preview_question_id"] = selected_question_id

    if selected_question_id:
        selected_row = progress_rows[selected_question_id]
        selected_answers_value = selected_row.get("answers", [])
        selected_answers = (
            selected_answers_value if isinstance(selected_answers_value, list) else []
        )
        st.markdown(f"#### {DISTILL_PAGE['raw_answer_title']}")
        st.caption(selected_row.get("question", ""))
        st.caption(
            "当前默认采样 2 个回答变体：分层盘点（更强调平台排序与优先级） / 来源增强（更强调来源显式度与证据抽取）。"
        )
        if not selected_answers:
            st.info(DISTILL_PAGE["raw_answer_empty"])
        else:
            for answer in selected_answers:
                variant_label = str(answer.get("prompt_variant", "")) or "未知变体"
                display_label = PROMPT_VARIANT_LABELS.get(variant_label, variant_label)
                variant_explanation = PROMPT_VARIANT_EXPLANATIONS.get(variant_label, "")
                text = escape(str(answer.get("text", "")))
                error = answer.get("error")
                st.markdown(
                    f"<div class='geo-answer-block'><div class='geo-answer-label'>{display_label}</div><div class='geo-answer-text'>{text}</div></div>",
                    unsafe_allow_html=True,
                )
                if variant_explanation:
                    st.caption(variant_explanation)
                if error:
                    st.error(str(error))

    if start_requested:
        with st.spinner(DISTILL_PAGE["spinner"]):
            job_meta = start_distillation_job(
                project_root=project_root,
                runs_dir=config.runs_dir,
                draft_path=Path(selected_draft["draft_path"]),
                benchmark_path=None,
            )

        st.session_state["active_distillation_job_id"] = job_meta["job_id"]
        st.session_state["active_distillation_job_meta"] = job_meta
        st.rerun()
