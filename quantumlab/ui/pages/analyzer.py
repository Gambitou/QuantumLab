from __future__ import annotations

import sqlite3

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from quantumlab.hypothesis_analyzer import analyze_hypotheses
from quantumlab.repositories import (
    create_relation,
    list_formulas,
    list_hypotheses,
    list_relations,
)


PRIORITY_COLORS = {
    "alta": "#fb7185",
    "media": "#f59e0b",
    "baja": "#22d3ee",
}


def _priority_badge(priority: str) -> str:
    color = PRIORITY_COLORS.get(priority, "#94a3b8")
    return (
        f'<span style="border:1px solid {color}; color:{color}; '
        'border-radius:999px; padding:0.08rem 0.5rem; font-size:0.76rem;">'
        f'{priority}</span>'
    )


def _similarity_heatmap(result) -> go.Figure:
    titles = [item["title"] for item in result.hypotheses]
    matrix = np.eye(len(titles))
    index_by_id = {item["id"]: index for index, item in enumerate(result.hypotheses)}
    for pair in result.similarity_pairs:
        left = index_by_id[pair["source_id"]]
        right = index_by_id[pair["target_id"]]
        matrix[left, right] = pair["score"]
        matrix[right, left] = pair["score"]

    figure = go.Figure(
        data=[
            go.Heatmap(
                z=matrix,
                x=titles,
                y=titles,
                zmin=0,
                zmax=1,
                colorscale="Viridis",
                colorbar={"title": "sim"},
            )
        ]
    )
    figure.update_layout(
        height=460,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1020",
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        font={"color": "#e5eefc"},
    )
    return figure


def _resonance_chart(result) -> go.Figure:
    data = result.resonance[:12]
    colors = [PRIORITY_COLORS[item["priority"]] for item in data]
    figure = go.Figure(
        data=[
            go.Bar(
                x=[item["score"] for item in data],
                y=[item["title"] for item in data],
                orientation="h",
                marker={"color": colors},
                customdata=[
                    [item["semantic"], item["relations"], item["formulas"]]
                    for item in data
                ],
                hovertemplate=(
                    "Resonance %{x}<br>"
                    "Semantica %{customdata[0]}%<br>"
                    "Relaciones %{customdata[1]}<br>"
                    "Formulas %{customdata[2]}<extra></extra>"
                ),
            )
        ]
    )
    figure.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1020",
        xaxis={"range": [0, 100], "gridcolor": "#283247"},
        yaxis={"gridcolor": "#283247", "autorange": "reversed"},
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        font={"color": "#e5eefc"},
    )
    return figure


def _cluster_scatter(result) -> go.Figure:
    x_values = []
    y_values = []
    sizes = []
    labels = []
    terms = []
    for cluster in result.clusters:
        x_values.append(cluster["id"])
        y_values.append(cluster["size"])
        sizes.append(18 + cluster["size"] * 8)
        labels.append(f'Cluster {cluster["id"]}')
        terms.append(", ".join(cluster["terms"]) or "sin terminos")
    figure = go.Figure(
        data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="markers+text",
                text=labels,
                textposition="top center",
                marker={"size": sizes, "color": "#22d3ee", "line": {"color": "#e5eefc", "width": 1}},
                customdata=terms,
                hovertemplate="%{text}<br>tamano %{y}<br>%{customdata}<extra></extra>",
            )
        ]
    )
    figure.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1020",
        xaxis={"title": "cluster", "gridcolor": "#283247", "dtick": 1},
        yaxis={"title": "hipotesis", "gridcolor": "#283247"},
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        font={"color": "#e5eefc"},
    )
    return figure


def _render_insights(result) -> None:
    st.subheader("Insights")
    if not result.insights:
        st.info("No hay insights automaticos todavia.")
        return

    for insight in result.insights:
        with st.container(border=True):
            st.markdown(
                f'{_priority_badge(insight["priority"])} **{insight["title"]}**',
                unsafe_allow_html=True,
            )
            st.write(insight["body"])


def _render_connections(result) -> None:
    st.subheader("Indicadores de conexion")
    if not result.similarity_pairs and not result.concept_links:
        st.info("No hay conexiones fuertes detectadas.")
        return

    for pair in result.similarity_pairs[:10]:
        with st.container(border=True):
            st.markdown(
                f'{_priority_badge(pair["priority"])} **{pair["source_title"]} -> {pair["target_title"]}**',
                unsafe_allow_html=True,
            )
            st.progress(min(1.0, pair["score"]))
            st.caption(f'Similitud semantica: {pair["score"]:.2f}')
            if st.button(
                "Guardar como relacion",
                key=f'analyzer_relation_{pair["source_id"]}_{pair["target_id"]}',
            ):
                try:
                    create_relation(
                        pair["source_id"],
                        pair["target_id"],
                        f'analisis semantico {round(pair["score"] * 100)}%',
                        "Relacion sugerida por Hypothesis Analyzer.",
                        max(pair["score"], 0.2),
                    )
                except sqlite3.IntegrityError:
                    st.warning("La relacion ya existe con esa etiqueta.")
                else:
                    st.success("Relacion guardada.")
                    st.rerun()

    if result.concept_links:
        st.markdown("**Conceptos compartidos**")
        for link in result.concept_links[:8]:
            st.caption(
                f'{link["source_title"]} -> {link["target_title"]}: {", ".join(link["concepts"])}'
            )


def _render_conflicts(result) -> None:
    st.subheader("Consistencia logica")
    if not result.contradictions:
        st.success("No se detectaron contradicciones simples.")
        return

    for conflict in result.contradictions:
        with st.container(border=True):
            st.markdown(
                f'{_priority_badge(conflict["priority"])} **{conflict["source_title"]} vs {conflict["target_title"]}**',
                unsafe_allow_html=True,
            )
            st.write(f'Terminos en tension: {", ".join(conflict["terms"])}')
            st.caption(f'Similitud contextual: {conflict["score"]:.2f}')


def _render_math(result) -> None:
    st.subheader("Asistencia matematica")
    if not result.math_matches:
        st.info("No se detectaron formulas ni conceptos matematicos claros.")
        return

    for item in result.math_matches:
        with st.container(border=True):
            st.markdown(f'**{item["title"]}**')
            if item["concepts"]:
                st.caption("Conceptos: " + ", ".join(item["concepts"]))
            if item["formulas"]:
                st.write("Formulas detectadas:")
                for formula in item["formulas"]:
                    st.code(formula)
            if item["linked_formulas"]:
                st.write("Formulas guardadas relacionadas:")
                for formula in item["linked_formulas"]:
                    st.latex(formula["latex"])
            if item["suggestions"]:
                st.write("Ecuaciones sugeridas:")
                for suggestion in item["suggestions"]:
                    st.code(suggestion)


def _render_clusters(result) -> None:
    st.subheader("Clusters conceptuales")
    if not result.clusters:
        st.info("No hay clusters para visualizar.")
        return

    st.plotly_chart(_cluster_scatter(result), use_container_width=True)
    for cluster in result.clusters:
        with st.expander(f'Cluster {cluster["id"]} - {cluster["size"]} hipotesis'):
            st.caption("Terminos dominantes: " + (", ".join(cluster["terms"]) or "sin terminos"))
            for title in cluster["titles"]:
                st.write(title)


def render_hypothesis_analyzer() -> None:
    st.title("Hypothesis Analyzer")

    hypotheses = list_hypotheses()
    relations = list_relations()
    formulas = list_formulas()

    if not hypotheses:
        st.info("Crea hipotesis para iniciar el analisis.")
        return

    threshold = st.slider("Sensibilidad semantica", 0.10, 0.80, 0.26, 0.02)
    result = analyze_hypotheses(hypotheses, relations, formulas, threshold)

    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("Hipotesis", len(hypotheses))
    metric_b.metric("Conexiones", len(result.similarity_pairs))
    metric_c.metric("Conflictos", len(result.contradictions))
    metric_d.metric("Provider", result.provider_mode)

    st.divider()

    overview, insights, consistency, math_tab, clusters = st.tabs(
        [
            "Panel visual",
            "Insights",
            "Consistencia",
            "Matematica",
            "Clusters",
        ]
    )

    with overview:
        left, right = st.columns((1.05, 1))
        with left:
            st.subheader("Idea Resonance")
            st.plotly_chart(_resonance_chart(result), use_container_width=True)
        with right:
            st.subheader("Mapa semantico")
            st.plotly_chart(_similarity_heatmap(result), use_container_width=True)
        _render_connections(result)

    with insights:
        _render_insights(result)

    with consistency:
        _render_conflicts(result)

    with math_tab:
        _render_math(result)

    with clusters:
        _render_clusters(result)
