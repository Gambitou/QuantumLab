from __future__ import annotations

import itertools
import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

import networkx as nx
import numpy as np

from quantumlab.ai.providers import get_embedding_provider


CONTRADICTION_PATTERNS = (
    (("no", "nunca", "imposible", "ausencia", "niega"), ("siempre", "posible", "presencia", "afirma")),
    (("discret*", "cuantiz*", "digital"), ("continu*", "analogic*")),
    (("determin*", "causal"), ("aleatori*", "azar", "estocastic*")),
    (("local", "sin accion a distancia"), ("no local", "entrelazado", "accion a distancia")),
    (("conserv*",), ("disip*", "perdida", "decae")),
)

MATH_CONCEPTS = {
    "derivada": ("derivada", "gradiente", "diferencial", "tasa"),
    "ecuacion diferencial": ("ode", "diferencial", "dinamico", "evolucion"),
    "probabilidad": ("probabilidad", "distribucion", "bayes", "azar", "estocastico"),
    "matriz": ("matriz", "vector", "eigen", "autovalor", "operador"),
    "energia": ("energia", "hamiltoniano", "lagrangiano", "accion"),
    "onda": ("onda", "frecuencia", "amplitud", "fase", "interferencia"),
    "informacion": ("informacion", "entropia", "canal", "senal"),
    "limite": ("limite", "convergencia", "asintotico"),
    "topologia": ("topologia", "red", "grafo", "conectividad"),
    "cuantizacion": ("cuantizacion", "cuantico", "discreto", "nivel"),
}

FORMULA_PATTERN = re.compile(
    r"(\$\$.*?\$\$|\$.*?\$|\\\(.+?\\\)|\\\[.+?\\\]|[A-Za-z][A-Za-z0-9_]*\s*=\s*[^.;,\n]+)",
    re.DOTALL,
)


@dataclass(frozen=True)
class AnalyzerResult:
    provider_mode: str
    hypotheses: list[dict[str, Any]]
    similarity_pairs: list[dict[str, Any]]
    clusters: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    math_matches: list[dict[str, Any]]
    insights: list[dict[str, Any]]
    resonance: list[dict[str, Any]]
    concept_links: list[dict[str, Any]]


def analyze_hypotheses(
    hypotheses: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    formulas: list[dict[str, Any]],
    similarity_threshold: float = 0.26,
) -> AnalyzerResult:
    provider = get_embedding_provider()
    if not hypotheses:
        return AnalyzerResult(provider.mode, [], [], [], [], [], [], [], [])

    texts = [_hypothesis_text(item) for item in hypotheses]
    vectors = provider.encode(texts)
    similarity = vectors @ vectors.T
    id_to_index = {item["id"]: index for index, item in enumerate(hypotheses)}

    similarity_pairs = _similarity_pairs(hypotheses, similarity, similarity_threshold)
    concept_links = _concept_links(hypotheses)
    clusters = _clusters(hypotheses, similarity_pairs, concept_links)
    contradictions = _contradictions(hypotheses, similarity)
    math_matches = _math_matches(hypotheses, formulas)
    resonance = _idea_resonance(hypotheses, relations, formulas, similarity, id_to_index)
    insights = _insights(hypotheses, similarity_pairs, contradictions, math_matches, resonance)

    return AnalyzerResult(
        provider.mode,
        hypotheses,
        similarity_pairs,
        clusters,
        contradictions,
        math_matches,
        insights,
        resonance,
        concept_links,
    )


def _hypothesis_text(item: dict[str, Any]) -> str:
    return f'{item["title"]}. {item["summary"]}. {item["tags"]}'


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return normalized.encode("ascii", "ignore").decode("ascii")


def _tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", _normalize_text(text)) if len(token) > 2]


def _has_term(text: str, term: str) -> bool:
    if term.endswith("*"):
        root = re.escape(term[:-1])
        return re.search(r"(?<![a-z0-9])" + root + r"[a-z0-9]*", text) is not None
    pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def _similarity_pairs(
    hypotheses: list[dict[str, Any]],
    similarity: np.ndarray,
    threshold: float,
) -> list[dict[str, Any]]:
    pairs = []
    for left_index, right_index in itertools.combinations(range(len(hypotheses)), 2):
        score = float(similarity[left_index, right_index])
        if score >= threshold:
            pairs.append(
                {
                    "source_id": hypotheses[left_index]["id"],
                    "source_title": hypotheses[left_index]["title"],
                    "target_id": hypotheses[right_index]["id"],
                    "target_title": hypotheses[right_index]["title"],
                    "score": score,
                    "priority": _priority(score, 0.72, 0.46),
                }
            )
    return sorted(pairs, key=lambda item: item["score"], reverse=True)


def _concept_links(hypotheses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    concepts_by_id: dict[int, set[str]] = {}
    for item in hypotheses:
        tokens = set(_tokens(_hypothesis_text(item)))
        tags = {tag.strip().lower() for tag in item.get("tags", "").split(",") if tag.strip()}
        concepts_by_id[item["id"]] = tokens.union(tags)

    links = []
    by_id = {item["id"]: item for item in hypotheses}
    for left_id, right_id in itertools.combinations(concepts_by_id, 2):
        shared = sorted(concepts_by_id[left_id].intersection(concepts_by_id[right_id]))
        shared = [token for token in shared if len(token) > 3][:8]
        if shared:
            links.append(
                {
                    "source_id": left_id,
                    "source_title": by_id[left_id]["title"],
                    "target_id": right_id,
                    "target_title": by_id[right_id]["title"],
                    "concepts": shared,
                    "strength": min(1.0, len(shared) / 6.0),
                }
            )
    return sorted(links, key=lambda item: item["strength"], reverse=True)


def _clusters(
    hypotheses: list[dict[str, Any]],
    similarity_pairs: list[dict[str, Any]],
    concept_links: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    graph = nx.Graph()
    for item in hypotheses:
        graph.add_node(item["id"], title=item["title"])
    for pair in similarity_pairs:
        graph.add_edge(pair["source_id"], pair["target_id"], weight=pair["score"])
    for link in concept_links:
        if link["strength"] >= 0.34:
            graph.add_edge(link["source_id"], link["target_id"], weight=link["strength"])

    by_id = {item["id"]: item for item in hypotheses}
    clusters = []
    for index, component in enumerate(sorted(nx.connected_components(graph), key=len, reverse=True), start=1):
        node_ids = sorted(component)
        words = Counter()
        for node_id in node_ids:
            words.update(_tokens(_hypothesis_text(by_id[node_id])))
        common_terms = [word for word, _count in words.most_common(6)]
        clusters.append(
            {
                "id": index,
                "size": len(node_ids),
                "node_ids": node_ids,
                "titles": [by_id[node_id]["title"] for node_id in node_ids],
                "terms": common_terms,
            }
        )
    return clusters


def _contradictions(
    hypotheses: list[dict[str, Any]],
    similarity: np.ndarray,
) -> list[dict[str, Any]]:
    findings = []
    for left_index, right_index in itertools.combinations(range(len(hypotheses)), 2):
        left_text = _normalize_text(_hypothesis_text(hypotheses[left_index]))
        right_text = _normalize_text(_hypothesis_text(hypotheses[right_index]))
        score = float(similarity[left_index, right_index])
        for left_terms, right_terms in CONTRADICTION_PATTERNS:
            left_has_a = [term for term in left_terms if _has_term(left_text, term)]
            left_has_b = [term for term in right_terms if _has_term(left_text, term)]
            right_has_a = [term for term in left_terms if _has_term(right_text, term)]
            right_has_b = [term for term in right_terms if _has_term(right_text, term)]
            if (left_has_a and right_has_b) or (left_has_b and right_has_a):
                terms = sorted({term.rstrip("*") for term in left_has_a + left_has_b + right_has_a + right_has_b})
                findings.append(
                    {
                        "source_id": hypotheses[left_index]["id"],
                        "source_title": hypotheses[left_index]["title"],
                        "target_id": hypotheses[right_index]["id"],
                        "target_title": hypotheses[right_index]["title"],
                        "terms": terms,
                        "score": score,
                        "priority": "alta" if score >= 0.25 else "media",
                    }
                )
                break
    return sorted(findings, key=lambda item: (item["priority"] != "alta", -item["score"]))


def _math_matches(
    hypotheses: list[dict[str, Any]],
    formulas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    formulas_by_hypothesis = defaultdict(list)
    for formula in formulas:
        if formula.get("hypothesis_id"):
            formulas_by_hypothesis[formula["hypothesis_id"]].append(formula)

    matches = []
    for item in hypotheses:
        text = _hypothesis_text(item)
        normalized = _normalize_text(text)
        detected_formulas = [value.strip() for value in FORMULA_PATTERN.findall(text)]
        concepts = [
            concept
            for concept, terms in MATH_CONCEPTS.items()
            if any(term in normalized for term in terms)
        ]
        linked_formulas = formulas_by_hypothesis[item["id"]]
        suggestions = _equation_suggestions(concepts)
        if detected_formulas or concepts or linked_formulas:
            matches.append(
                {
                    "hypothesis_id": item["id"],
                    "title": item["title"],
                    "formulas": detected_formulas,
                    "linked_formulas": linked_formulas,
                    "concepts": concepts,
                    "suggestions": suggestions,
                }
            )
    return matches


def _equation_suggestions(concepts: list[str]) -> list[str]:
    suggestions = []
    if "energia" in concepts:
        suggestions.append("E = mc^2, H = T + V")
    if "onda" in concepts:
        suggestions.append("psi(x,t), omega = 2*pi*f")
    if "probabilidad" in concepts:
        suggestions.append("P(A|B) = P(B|A)P(A)/P(B)")
    if "ecuacion diferencial" in concepts:
        suggestions.append("dx/dt = f(x,t)")
    if "informacion" in concepts:
        suggestions.append("H(X) = -sum p(x) log p(x)")
    if "cuantizacion" in concepts:
        suggestions.append("E_n = h*f*(n + 1/2)")
    return suggestions[:4]


def _idea_resonance(
    hypotheses: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    formulas: list[dict[str, Any]],
    similarity: np.ndarray,
    id_to_index: dict[int, int],
) -> list[dict[str, Any]]:
    relation_degree = Counter()
    for relation in relations:
        relation_degree[relation["source_hypothesis_id"]] += 1
        relation_degree[relation["target_hypothesis_id"]] += 1
    formula_count = Counter(formula["hypothesis_id"] for formula in formulas if formula.get("hypothesis_id"))
    max_degree = max(relation_degree.values(), default=1)
    max_formulas = max(formula_count.values(), default=1)

    resonance = []
    for item in hypotheses:
        index = id_to_index[item["id"]]
        similarity_values = np.delete(similarity[index], index)
        semantic_score = float(np.mean(np.clip(similarity_values, 0, 1))) if len(similarity_values) else 0.0
        graph_score = relation_degree[item["id"]] / max_degree if max_degree else 0.0
        formula_score = formula_count[item["id"]] / max_formulas if max_formulas else 0.0
        tag_score = min(1.0, len([tag for tag in item.get("tags", "").split(",") if tag.strip()]) / 5.0)
        score = 100 * (0.46 * semantic_score + 0.28 * graph_score + 0.16 * formula_score + 0.10 * tag_score)
        resonance.append(
            {
                "hypothesis_id": item["id"],
                "title": item["title"],
                "score": round(score, 1),
                "semantic": round(semantic_score * 100, 1),
                "relations": relation_degree[item["id"]],
                "formulas": formula_count[item["id"]],
                "priority": _priority(score, 65, 35),
            }
        )
    return sorted(resonance, key=lambda item: item["score"], reverse=True)


def _insights(
    hypotheses: list[dict[str, Any]],
    similarity_pairs: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
    math_matches: list[dict[str, Any]],
    resonance: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    insights = []
    for pair in similarity_pairs[:5]:
        insights.append(
            {
                "type": "conexion",
                "priority": pair["priority"],
                "title": "Conexion semantica fuerte",
                "body": f'{pair["source_title"]} y {pair["target_title"]} comparten una resonancia semantica de {pair["score"]:.2f}.',
            }
        )
    for conflict in contradictions[:5]:
        insights.append(
            {
                "type": "conflicto",
                "priority": conflict["priority"],
                "title": "Posible contradiccion conceptual",
                "body": f'{conflict["source_title"]} y {conflict["target_title"]} usan terminos tensionados: {", ".join(conflict["terms"])}.',
            }
        )
    math_by_id = {item["hypothesis_id"]: item for item in math_matches}
    for item in hypotheses:
        summary = item.get("summary", "").strip()
        if len(summary) < 60:
            insights.append(
                {
                    "type": "incompleta",
                    "priority": "media",
                    "title": "Hipotesis incompleta",
                    "body": f'{item["title"]} podria necesitar condiciones, variables o criterios de falsacion mas explicitos.',
                }
            )
        if item["id"] not in math_by_id and any(token in _normalize_text(_hypothesis_text(item)) for token in ("cuant", "energia", "sistema", "dinam")):
            insights.append(
                {
                    "type": "matematica",
                    "priority": "baja",
                    "title": "Formalizacion sugerida",
                    "body": f'{item["title"]} parece admitir una formulacion matematica o una simulacion en Reality Engine.',
                }
            )
    for item in resonance[:3]:
        insights.append(
            {
                "type": "resonance",
                "priority": item["priority"],
                "title": "Idea Resonance alta",
                "body": f'{item["title"]} esta conectada con el sistema en {item["score"]}/100. Puede ser un buen eje de investigacion.',
            }
        )
    if len(hypotheses) >= 2 and not similarity_pairs:
        insights.append(
            {
                "type": "exploracion",
                "priority": "media",
                "title": "Islas conceptuales",
                "body": "Las hipotesis actuales parecen poco conectadas. Conviene agregar etiquetas, variables compartidas o relaciones manuales.",
            }
        )
    return insights[:18]


def _priority(value: float, high: float, medium: float) -> str:
    if value >= high:
        return "alta"
    if value >= medium:
        return "media"
    return "baja"
