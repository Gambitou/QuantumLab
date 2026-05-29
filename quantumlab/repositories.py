from __future__ import annotations

import json
import math
import re
import unicodedata
from typing import Any

from quantumlab.database import get_connection


STATUS_OPTIONS = ("Borrador", "En estudio", "Validada", "Descartada")


def _rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def create_hypothesis(title: str, summary: str, status: str, tags: str) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO hypotheses (title, summary, status, tags)
            VALUES (?, ?, ?, ?)
            """,
            (title.strip(), summary.strip(), status, tags.strip()),
        )
        return int(cursor.lastrowid)


def list_hypotheses() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                h.*,
                COUNT(f.id) AS formula_count
            FROM hypotheses h
            LEFT JOIN formulas f ON f.hypothesis_id = h.id
            GROUP BY h.id
            ORDER BY h.updated_at DESC, h.id DESC
            """
        ).fetchall()
        return _rows_to_dicts(rows)


def update_hypothesis(
    hypothesis_id: int,
    title: str,
    summary: str,
    status: str,
    tags: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE hypotheses
            SET title = ?, summary = ?, status = ?, tags = ?
            WHERE id = ?
            """,
            (title.strip(), summary.strip(), status, tags.strip(), hypothesis_id),
        )


def delete_hypothesis(hypothesis_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM hypotheses WHERE id = ?", (hypothesis_id,))


def create_formula(
    title: str,
    latex: str,
    notes: str,
    hypothesis_id: int | None,
) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO formulas (title, latex, notes, hypothesis_id)
            VALUES (?, ?, ?, ?)
            """,
            (title.strip(), latex.strip(), notes.strip(), hypothesis_id),
        )
        return int(cursor.lastrowid)


def list_formulas() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                f.*,
                h.title AS hypothesis_title
            FROM formulas f
            LEFT JOIN hypotheses h ON h.id = f.hypothesis_id
            ORDER BY f.updated_at DESC, f.id DESC
            """
        ).fetchall()
        return _rows_to_dicts(rows)


def delete_formula(formula_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM formulas WHERE id = ?", (formula_id,))


def _normalize_relation_ids(source_id: int, target_id: int) -> tuple[int, int]:
    return (source_id, target_id) if source_id < target_id else (target_id, source_id)


def create_relation(
    source_hypothesis_id: int,
    target_hypothesis_id: int,
    label: str,
    notes: str = "",
    weight: float = 1.0,
) -> int:
    source_id, target_id = _normalize_relation_ids(source_hypothesis_id, target_hypothesis_id)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO hypothesis_relations (
                source_hypothesis_id,
                target_hypothesis_id,
                label,
                notes,
                weight
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_id, target_id, label.strip(), notes.strip(), float(weight)),
        )
        return int(cursor.lastrowid)


def relation_exists(source_hypothesis_id: int, target_hypothesis_id: int) -> bool:
    source_id, target_id = _normalize_relation_ids(source_hypothesis_id, target_hypothesis_id)
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM hypothesis_relations
            WHERE source_hypothesis_id = ? AND target_hypothesis_id = ?
            LIMIT 1
            """,
            (source_id, target_id),
        ).fetchone()
        return row is not None


def list_relations() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                r.*,
                source.title AS source_title,
                target.title AS target_title
            FROM hypothesis_relations r
            JOIN hypotheses source ON source.id = r.source_hypothesis_id
            JOIN hypotheses target ON target.id = r.target_hypothesis_id
            ORDER BY r.updated_at DESC, r.id DESC
            """
        ).fetchall()
        return _rows_to_dicts(rows)


def delete_relation(relation_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM hypothesis_relations WHERE id = ?", (relation_id,))


def save_reality_simulation(
    title: str,
    simulation_type: str,
    parameters: dict[str, Any],
    summary: str,
) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO reality_simulations (
                title,
                simulation_type,
                parameters,
                summary
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title.strip(),
                simulation_type.strip(),
                json.dumps(parameters, ensure_ascii=True, sort_keys=True),
                summary.strip(),
            ),
        )
        return int(cursor.lastrowid)


def list_reality_simulations() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM reality_simulations
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    simulations = _rows_to_dicts(rows)
    for item in simulations:
        try:
            item["parameters_data"] = json.loads(item["parameters"])
        except json.JSONDecodeError:
            item["parameters_data"] = {}
    return simulations


def delete_reality_simulation(simulation_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM reality_simulations WHERE id = ?", (simulation_id,))


def _tokens_for_similarity(item: dict[str, Any]) -> list[str]:
    text = f'{item["title"]} {item["summary"]} {item["tags"]}'.lower()
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return [token for token in re.findall(r"[a-z0-9]+", ascii_text) if len(token) > 2]


def _term_vector(tokens: list[str]) -> dict[str, float]:
    vector: dict[str, float] = {}
    for token in tokens:
        vector[token] = vector.get(token, 0.0) + 1.0
    return vector


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    common_terms = set(left).intersection(right)
    dot = sum(left[term] * right[term] for term in common_terms)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def suggest_similar_hypotheses(
    threshold: float = 0.18,
    limit: int = 8,
) -> list[dict[str, Any]]:
    hypotheses = list_hypotheses()
    vectors = {
        item["id"]: _term_vector(_tokens_for_similarity(item))
        for item in hypotheses
    }
    suggestions: list[dict[str, Any]] = []

    for left_index, left in enumerate(hypotheses):
        for right in hypotheses[left_index + 1 :]:
            if relation_exists(left["id"], right["id"]):
                continue
            score = _cosine_similarity(vectors[left["id"]], vectors[right["id"]])
            if score >= threshold:
                suggestions.append(
                    {
                        "source_id": left["id"],
                        "source_title": left["title"],
                        "target_id": right["id"],
                        "target_title": right["title"],
                        "score": score,
                    }
                )

    return sorted(suggestions, key=lambda item: item["score"], reverse=True)[:limit]


def dashboard_metrics() -> dict[str, int]:
    with get_connection() as connection:
        hypotheses = connection.execute("SELECT COUNT(*) FROM hypotheses").fetchone()[0]
        formulas = connection.execute("SELECT COUNT(*) FROM formulas").fetchone()[0]
        relations = connection.execute("SELECT COUNT(*) FROM hypothesis_relations").fetchone()[0]
        simulations = connection.execute("SELECT COUNT(*) FROM reality_simulations").fetchone()[0]
        active = connection.execute(
            "SELECT COUNT(*) FROM hypotheses WHERE status IN ('Borrador', 'En estudio')"
        ).fetchone()[0]

    return {
        "hypotheses": int(hypotheses),
        "formulas": int(formulas),
        "relations": int(relations),
        "simulations": int(simulations),
        "active": int(active),
    }
