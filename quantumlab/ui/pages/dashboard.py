from html import escape

import streamlit as st

from quantumlab.repositories import dashboard_metrics, list_formulas, list_hypotheses


def render_dashboard() -> None:
    st.title("Panel de investigacion")

    metrics = dashboard_metrics()
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    col_a.metric("Hipotesis", metrics["hypotheses"])
    col_b.metric("Formulas", metrics["formulas"])
    col_c.metric("Relaciones", metrics["relations"])
    col_d.metric("Simulaciones", metrics["simulations"])
    col_e.metric("Activas", metrics["active"])

    st.divider()

    left, right = st.columns((1.2, 1))
    with left:
        st.subheader("Hipotesis recientes")
        hypotheses = list_hypotheses()[:5]
        if not hypotheses:
            st.info("Aun no hay hipotesis guardadas.")
        for item in hypotheses:
            st.markdown(
                f"""
                <div class="ql-record">
                    <div class="ql-record-title">{escape(item["title"])}</div>
                    <div class="ql-meta">{escape(item["status"])} - {item["formula_count"]} formulas - {item["updated_at"]}</div>
                    <div>{escape(item["summary"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.subheader("Formulas recientes")
        formulas = list_formulas()[:5]
        if not formulas:
            st.info("Aun no hay formulas guardadas.")
        for item in formulas:
            st.markdown(
                f"""
                <div class="ql-record">
                    <div class="ql-record-title">{escape(item["title"])}</div>
                    <div class="ql-meta">{escape(item["hypothesis_title"] or "Sin hipotesis")} - {item["updated_at"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.latex(item["latex"])
