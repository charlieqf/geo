# pyright: reportMissingImports=false

from __future__ import annotations

import streamlit as st

from src.ui_helpers import app_css
from src.ui_copy import METHODOLOGY_PAGE


st.set_page_config(page_title=METHODOLOGY_PAGE["page_title"], layout="wide")
st.markdown(app_css(), unsafe_allow_html=True)

st.markdown(f"### {METHODOLOGY_PAGE['heading']}")
st.markdown(METHODOLOGY_PAGE["body"])
