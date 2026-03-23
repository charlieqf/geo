# pyright: reportMissingImports=false

from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.services.run_service import format_run_label, list_runs
from src.ui_helpers import app_css
from src.ui_copy import APP_TITLE, HOME_PAGE


st.set_page_config(page_title=HOME_PAGE["page_title"], layout="wide")
st.markdown(app_css(), unsafe_allow_html=True)

config = load_config()
runs = list_runs(config.runs_dir)

st.markdown(
    f"""
    <div class="geo-hero">
      <h1>{APP_TITLE}</h1>
      <div class="geo-muted">{HOME_PAGE["hero_subtitle"]}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"<div class='geo-kpi'><div class='geo-kpi-label'>{HOME_PAGE['kpi_target']}</div><div class='geo-kpi-value'>豆包</div></div>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"<div class='geo-kpi'><div class='geo-kpi-label'>{HOME_PAGE['kpi_model']}</div><div class='geo-kpi-value'>{config.openai_model}</div></div>",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"<div class='geo-kpi'><div class='geo-kpi-label'>{HOME_PAGE['kpi_runs']}</div><div class='geo-kpi-value'>{len(runs)}</div></div>",
        unsafe_allow_html=True,
    )

st.write("")
left, right = st.columns([1.2, 1])

with left:
    st.markdown(f"### {HOME_PAGE['workflow_title']}")
    st.markdown(
        "<div class='geo-section-card'><ol class='geo-list'>"
        + "".join(f"<li>{step}</li>" for step in HOME_PAGE["workflow_steps"])
        + "</ol></div>",
        unsafe_allow_html=True,
    )
    st.caption(HOME_PAGE["advanced_settings_hint"])

with right:
    st.markdown(f"### {HOME_PAGE['latest_runs_title']}")
    if not runs:
        st.info(HOME_PAGE["no_runs"])
    for run in runs[:5]:
        top_platforms = ", ".join(
            name for name, _ in run["top_actionable_platforms"][:4]
        )
        st.markdown(
            f"""
            <div class="geo-card">
              <strong>{format_run_label(run["run_id"])}</strong><br/>
              <span class="geo-muted">{HOME_PAGE["top_platforms_prefix"]}{top_platforms or "暂无"}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
