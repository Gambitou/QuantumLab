import streamlit as st

from quantumlab import APP_NAME
from quantumlab.ui.pages.analyzer import render_hypothesis_analyzer
from quantumlab.ui.pages.dashboard import render_dashboard
from quantumlab.ui.pages.formulas import render_formulas
from quantumlab.ui.pages.hypotheses import render_hypotheses
from quantumlab.ui.pages.relations import render_relations
from quantumlab.ui.pages.reality import render_reality_engine
from quantumlab.ui.styles import apply_dark_theme


PAGES = {
    "Panel": render_dashboard,
    "Hipotesis": render_hypotheses,
    "Hypothesis Analyzer": render_hypothesis_analyzer,
    "Relaciones": render_relations,
    "Reality Engine": render_reality_engine,
    "Formulas LaTeX": render_formulas,
}


def render_app() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=":material/science:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_dark_theme()

    with st.sidebar:
        st.title(APP_NAME)
        st.caption("Laboratorio local")
        page_name = st.radio("Navegacion", list(PAGES), label_visibility="collapsed")

    PAGES[page_name]()
