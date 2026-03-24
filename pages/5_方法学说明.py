# pyright: reportMissingImports=false

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.ui_helpers import app_css
from src.ui_copy import METHODOLOGY_PAGE


st.set_page_config(page_title=METHODOLOGY_PAGE["page_title"], layout="wide")
st.markdown(app_css(), unsafe_allow_html=True)

st.markdown(f"### {METHODOLOGY_PAGE['heading']}")
doc_path = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "methodology"
    / "03-system-methodology.md"
)
body = (
    doc_path.read_text(encoding="utf-8")
    if doc_path.exists()
    else METHODOLOGY_PAGE["body"]
)
st.markdown(body)
