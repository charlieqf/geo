# pyright: reportMissingImports=false

from __future__ import annotations

from html import escape

import streamlit as st

from src.config import load_config
from src.pipeline.question_generation import (
    generate_question_draft,
    load_question_generation_config,
)
from src.providers.openai_client import OpenAIAnalysisClient
from src.services.draft_service import format_draft_label, list_question_drafts
from src.services.prompt_meta_service import load_prompt_meta
from src.ui_helpers import app_css
from src.ui_copy import QUESTION_PAGE


st.set_page_config(page_title=QUESTION_PAGE["page_title"], layout="wide")
st.markdown(app_css(), unsafe_allow_html=True)

config = load_config()
drafts_dir = config.runs_dir / "question_drafts"
st.markdown(f"### {QUESTION_PAGE['heading']}")

prompt_meta = load_prompt_meta(config.prompts_dir / "question_pool_prompt.json")
question_config = load_question_generation_config(config.prompts_dir)


generator_tab, prompt_tab = st.tabs(
    [QUESTION_PAGE["generator_tab"], QUESTION_PAGE["prompt_tab"]]
)

with prompt_tab:
    prompt_system_tab, prompt_user_tab, prompt_meta_tab = st.tabs(
        [
            QUESTION_PAGE["prompt_system_title"],
            QUESTION_PAGE["prompt_user_title"],
            QUESTION_PAGE["prompt_meta_title"],
        ]
    )
    with prompt_system_tab:
        st.code(
            (config.prompts_dir / "question_pool_system.md").read_text(
                encoding="utf-8"
            ),
            language="markdown",
        )
    with prompt_user_tab:
        st.code(
            (config.prompts_dir / "question_pool_user.md").read_text(encoding="utf-8"),
            language="markdown",
        )
    with prompt_meta_tab:
        st.json(prompt_meta)

with generator_tab:
    st.markdown("<div class='geo-form-shell'>", unsafe_allow_html=True)
    with st.form("generate-question-draft"):
        keyword_col, brand_col, count_col = st.columns(3)
        with keyword_col:
            keyword = st.text_input(
                QUESTION_PAGE["keyword_label"], value="中国 GEO 服务"
            )
        with brand_col:
            brand = st.text_input(QUESTION_PAGE["brand_label"], value="")
        with count_col:
            question_count = st.number_input(
                QUESTION_PAGE["question_count_label"],
                min_value=1,
                step=1,
                value=int(question_config["default_question_count"]),
                help=QUESTION_PAGE["question_count_help"].format(
                    brand_count=question_config["brand_question_count"]
                ),
            )
        submitted = st.form_submit_button(QUESTION_PAGE["submit_label"], type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        analyzer = OpenAIAnalysisClient(
            config.openai_api_key or "", config.openai_model
        )
        with st.spinner(QUESTION_PAGE["spinner"]):
            result = generate_question_draft(
                keyword=keyword,
                brand=brand,
                analyzer=analyzer,
                prompts_dir=config.prompts_dir,
                storage_dir=drafts_dir,
                question_count=int(question_count),
            )

        st.success(QUESTION_PAGE["success"])
        st.json(result)

    st.markdown(f"#### {QUESTION_PAGE['draft_title']}")
    st.caption(QUESTION_PAGE["draft_help"])
    drafts = list_question_drafts(drafts_dir)
    if not drafts:
        st.info(QUESTION_PAGE["draft_empty"])
    else:
        draft_map = {draft["draft_id"]: draft for draft in drafts}
        selected_draft_id = st.selectbox(
            QUESTION_PAGE["draft_selector"],
            list(draft_map.keys()),
            format_func=format_draft_label,
        )
        if selected_draft_id is None:
            selected_draft_id = next(iter(draft_map))
        selected = draft_map[selected_draft_id]
        st.markdown(
            f"<div class='geo-section-card'><strong>{selected['keyword']}</strong><br/><span class='geo-muted'>品牌：{selected.get('brand') or '未填写'} · {QUESTION_PAGE['draft_count']}：{selected['question_count']}</span></div>",
            unsafe_allow_html=True,
        )
        cards = []
        for item in selected.get("questions", []):
            group_label = (
                "品牌相关" if item.get("question_group") == "brand_specific" else "通用"
            )
            cards.append(
                f"""
                <div class="geo-question-card">
                  <div class="geo-question-meta">
                    <span class="geo-chip">{escape(str(item["question_id"]))}</span>
                    <span class="geo-chip">{group_label}</span>
                    <span class="geo-chip">{escape(str(item["intent_bucket"]))}</span>
                  </div>
                  <div class="geo-question-title">{escape(str(item["question"]))}</div>
                  <div class="geo-question-reason">生成原因：{escape(str(item["why_this_question"]))}</div>
                </div>
                """
            )
        st.html(f"<div class='geo-question-list-shell'>{''.join(cards)}</div>")
