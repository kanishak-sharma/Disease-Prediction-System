"""Entry point:  streamlit run app.py"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))  # so `core` and `views` import everywhere

st.set_page_config(page_title="Multi-Disease Prediction", page_icon="🩺", layout="wide",
                   initial_sidebar_state="collapsed")

from core.ui import footer, inject_css  # noqa: E402

inject_css()

pages = [
    st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("views/check.py", title="Health check", icon=":material/stethoscope:"),
    st.Page("views/insights.py", title="Model insights", icon=":material/monitoring:"),
    st.Page("views/library.py", title="Health guide", icon=":material/menu_book:"),
    st.Page("views/about.py", title="About", icon=":material/info:"),
]
st.navigation(pages, position="top").run()
footer()
