# pyright: reportMissingImports=false

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.config import load_config
from src.prompt_registry import PromptRegistry
from src.services.run_service import load_prompt_content, save_prompt_content
from src.ui_helpers import app_css
from src.ui_copy import PROMPT_LAB_PAGE, PROMPT_NAME_LABELS


st.set_page_config(page_title=PROMPT_LAB_PAGE["page_title"], layout="wide")
st.markdown(app_css(), unsafe_allow_html=True)

config = load_config()
registry = PromptRegistry(config.prompts_dir)
prompt_names = [definition.name for definition in registry.list_prompts()]
prompt_options = {PROMPT_NAME_LABELS.get(name, name): name for name in prompt_names}
selected_label = st.selectbox(
    PROMPT_LAB_PAGE["selector_label"], list(prompt_options.keys())
)
selected_name = prompt_options[selected_label]
prompt_path = Path(config.prompts_dir) / f"{selected_name}.md"
content = load_prompt_content(prompt_path)

st.markdown(f"### {PROMPT_LAB_PAGE['heading']}")
st.caption(PROMPT_LAB_PAGE["caption"])

st.markdown(
    f"<div class='geo-section-card'><strong>当前提示词</strong><br/><span class='geo-muted'>{selected_label}</span></div>",
    unsafe_allow_html=True,
)

edited = st.text_area(PROMPT_LAB_PAGE["editor_label"], value=content, height=520)
if st.button(PROMPT_LAB_PAGE["save_button"], type="primary"):
    save_prompt_content(prompt_path, edited)
    st.success(PROMPT_LAB_PAGE["save_success"].format(name=selected_name))
