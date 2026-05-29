from __future__ import annotations

import sqlite3

import streamlit as st
import streamlit.components.v1 as components

from quantumlab.relation_graph import (
    build_networkx_graph,
    cluster_summary,
    render_pyvis_html,
)
from quantumlab.repositories import (
    create_relation,
    delete_relation,
    list_hypotheses,
    list_relations,
    suggest_similar_hypotheses,
)


def _hypothesis_select_options(
    hypotheses: list[dict],
) -> tuple[list[str], dict[str, int]]:
    labels = [f'{item["title"]} #{item["id"]}' for item in hypotheses]
    mapping = {label: item["id"] for label, item in zip(labels, hypotheses)}
    return labels, mapping


def _render_manual_connection(hypotheses: list[dict]) -> None:
    st.subheader("Conexion manual")
    if len(hypotheses) < 2:
        st.info("Crea al menos dos hipotesis para conectarlas.")
        return

    labels, mapping = _hypothesis_select_options(hypotheses)
    with st.form("create_relation", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        source_label = col_a.selectbox("Hipotesis origen", labels)
        target_label = col_b.selectbox("Hipotesis destino", labels, index=1)
        relation_label = st.text_input(
            "Etiqueta de la conexion",
            placeholder="Ej. comparte mecanismo, contradice, deriva de",
        )
        notes = st.text_area("Notas", height=90)
        weight = st.slider("Fuerza de relacion", 0.2, 3.0, 1.0, 0.1)
        submitted = st.form_submit_button("Crear conexion", type="primary")

    if not submitted:
        return

    source_id = mapping[source_label]
    target_id = mapping[target_label]
    if source_id == target_id:
        st.error("Elige dos hipotesis distintas.")
        return
    if not relation_label.strip():
        st.error("La etiqueta de la conexion es obligatoria.")
        return

    try:
        create_relation(source_id, target_id, relation_label, notes, weight)
    except sqlite3.IntegrityError:
        st.warning("Esa conexion ya existe con la misma etiqueta.")
    else:
        st.success("Conexion guardada.")
        st.rerun()


def _render_suggestions() -> None:
    st.subheader("Sugerencias automaticas")
    suggestions = suggest_similar_hypotheses()
    if not suggestions:
        st.info("No hay pares similares sin conectar por ahora.")
        return

    for suggestion in suggestions:
        score = round(suggestion["score"] * 100)
        with st.container(border=True):
            st.write(
                f'{suggestion["source_title"]} -> {suggestion["target_title"]}'
            )
            st.caption(f"Similitud textual estimada: {score}%")
            if st.button(
                "Conectar sugerencia",
                key=f'suggest_{suggestion["source_id"]}_{suggestion["target_id"]}',
            ):
                create_relation(
                    suggestion["source_id"],
                    suggestion["target_id"],
                    f"similaridad {score}%",
                    "Relacion sugerida por similitud textual.",
                    max(suggestion["score"], 0.2),
                )
                st.success("Sugerencia conectada.")
                st.rerun()


def _render_clusters(hypotheses: list[dict], relations: list[dict]) -> None:
    graph = build_networkx_graph(hypotheses, relations)
    clusters = cluster_summary(graph)
    by_id = {item["id"]: item for item in hypotheses}
    related_clusters = [cluster for cluster in clusters if len(cluster) > 1]

    st.subheader("Clusters")
    if not related_clusters:
        st.info("Aun no hay clusters con mas de una hipotesis.")
        return

    for index, cluster in enumerate(related_clusters, start=1):
        names = ", ".join(by_id[node_id]["title"] for node_id in cluster)
        st.markdown(f"**Cluster {index}**")
        st.caption(names)


def _render_graph(hypotheses: list[dict], relations: list[dict]) -> None:
    st.subheader("Grafo interactivo")
    if not hypotheses:
        st.info("Crea hipotesis para iniciar el grafo.")
        return

    graph = build_networkx_graph(hypotheses, relations)
    components.html(render_pyvis_html(graph), height=650, scrolling=False)


def _render_relation_list(relations: list[dict]) -> None:
    st.subheader("Relaciones guardadas")
    if not relations:
        st.info("Aun no hay relaciones guardadas.")
        return

    for relation in relations:
        with st.container(border=True):
            st.write(
                f'{relation["source_title"]} -> {relation["target_title"]}'
            )
            st.caption(
                f'{relation["label"]} - peso {relation["weight"]:.1f} - {relation["updated_at"]}'
            )
            if relation["notes"]:
                st.write(relation["notes"])
            if st.button("Eliminar relacion", key=f'delete_relation_{relation["id"]}'):
                delete_relation(relation["id"])
                st.warning("Relacion eliminada.")
                st.rerun()


def render_relations() -> None:
    st.title("Relaciones")
    hypotheses = list_hypotheses()
    relations = list_relations()

    metric_a, metric_b, metric_c = st.columns(3)
    graph = build_networkx_graph(hypotheses, relations)
    connected_clusters = [cluster for cluster in cluster_summary(graph) if len(cluster) > 1]
    metric_a.metric("Nodos", len(hypotheses))
    metric_b.metric("Conexiones", len(relations))
    metric_c.metric("Clusters", len(connected_clusters))

    st.divider()
    left, right = st.columns((1, 1))
    with left:
        _render_manual_connection(hypotheses)
    with right:
        _render_suggestions()

    st.divider()
    _render_graph(hypotheses, relations)
    st.divider()

    col_a, col_b = st.columns((1, 1))
    with col_a:
        _render_clusters(hypotheses, relations)
    with col_b:
        _render_relation_list(relations)
