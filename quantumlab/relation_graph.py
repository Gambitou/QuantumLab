from __future__ import annotations

from html import escape
from typing import Any

import networkx as nx
from pyvis.network import Network


CLUSTER_COLORS = (
    "#22d3ee",
    "#a3e635",
    "#f59e0b",
    "#f472b6",
    "#818cf8",
    "#34d399",
    "#fb7185",
    "#c084fc",
)


def build_networkx_graph(
    hypotheses: list[dict[str, Any]],
    relations: list[dict[str, Any]],
) -> nx.Graph:
    graph = nx.Graph()

    for item in hypotheses:
        graph.add_node(
            item["id"],
            title=item["title"],
            status=item["status"],
            tags=item["tags"],
            summary=item["summary"],
        )

    for relation in relations:
        graph.add_edge(
            relation["source_hypothesis_id"],
            relation["target_hypothesis_id"],
            label=relation["label"],
            weight=relation["weight"],
            notes=relation["notes"],
        )

    return graph


def cluster_map(graph: nx.Graph) -> dict[int, int]:
    mapping: dict[int, int] = {}
    components = sorted(nx.connected_components(graph), key=len, reverse=True)
    for index, component in enumerate(components):
        for node_id in component:
            mapping[int(node_id)] = index
    return mapping


def cluster_summary(graph: nx.Graph) -> list[list[int]]:
    return [
        sorted(int(node_id) for node_id in component)
        for component in sorted(nx.connected_components(graph), key=len, reverse=True)
    ]


def render_pyvis_html(graph: nx.Graph) -> str:
    component_by_node = cluster_map(graph)
    network = Network(
        height="620px",
        width="100%",
        bgcolor="#0b1020",
        font_color="#e5eefc",
        cdn_resources="in_line",
    )
    network.barnes_hut(
        gravity=-36000,
        central_gravity=0.28,
        spring_length=145,
        spring_strength=0.025,
        damping=0.42,
    )

    for node_id, data in graph.nodes(data=True):
        cluster_id = component_by_node.get(int(node_id), 0)
        color = CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
        tags = f"<br><b>Etiquetas:</b> {escape(data.get('tags') or 'Sin etiquetas')}"
        summary = escape(data.get("summary") or "Sin resumen")
        title = (
            f"<b>{escape(data['title'])}</b><br>"
            f"<b>Estado:</b> {escape(data.get('status') or '')}"
            f"{tags}<br><br>{summary}"
        )
        network.add_node(
            int(node_id),
            label=data["title"],
            title=title,
            color={
                "background": color,
                "border": "#e5eefc",
                "highlight": {"background": "#ffffff", "border": color},
            },
            font={"color": "#e5eefc", "size": 16},
            shape="dot",
            size=24 if graph.degree(node_id) else 16,
            group=cluster_id,
        )

    for source_id, target_id, data in graph.edges(data=True):
        label = data.get("label") or "relacion"
        network.add_edge(
            int(source_id),
            int(target_id),
            label=label,
            title=escape(data.get("notes") or label),
            value=max(float(data.get("weight") or 1.0), 0.2),
            color="#94a3b8",
            font={"color": "#e5eefc", "size": 13, "strokeWidth": 4},
        )

    network.set_options(
        """
        {
          "nodes": {
            "borderWidth": 2,
            "shadow": { "enabled": true, "color": "rgba(0,0,0,0.35)" }
          },
          "edges": {
            "smooth": { "type": "dynamic" },
            "shadow": { "enabled": true, "color": "rgba(0,0,0,0.20)" }
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "tooltipDelay": 120
          },
          "physics": {
            "stabilization": { "iterations": 160 }
          }
        }
        """
    )

    return network.generate_html(notebook=False)
