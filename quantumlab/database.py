from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from quantumlab.config import DATA_DIR, DATABASE_PATH


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS hypotheses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Borrador',
                tags TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS formulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hypothesis_id INTEGER,
                title TEXT NOT NULL,
                latex TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hypothesis_id)
                    REFERENCES hypotheses (id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS hypothesis_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_hypothesis_id INTEGER NOT NULL,
                target_hypothesis_id INTEGER NOT NULL,
                label TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                weight REAL NOT NULL DEFAULT 1.0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CHECK (source_hypothesis_id <> target_hypothesis_id),
                UNIQUE (source_hypothesis_id, target_hypothesis_id, label),
                FOREIGN KEY (source_hypothesis_id)
                    REFERENCES hypotheses (id)
                    ON DELETE CASCADE,
                FOREIGN KEY (target_hypothesis_id)
                    REFERENCES hypotheses (id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS reality_simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                simulation_type TEXT NOT NULL,
                parameters TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TRIGGER IF NOT EXISTS update_hypotheses_timestamp
            AFTER UPDATE ON hypotheses
            FOR EACH ROW
            BEGIN
                UPDATE hypotheses
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = OLD.id;
            END;

            CREATE TRIGGER IF NOT EXISTS update_formulas_timestamp
            AFTER UPDATE ON formulas
            FOR EACH ROW
            BEGIN
                UPDATE formulas
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = OLD.id;
            END;

            CREATE TRIGGER IF NOT EXISTS update_hypothesis_relations_timestamp
            AFTER UPDATE ON hypothesis_relations
            FOR EACH ROW
            BEGIN
                UPDATE hypothesis_relations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = OLD.id;
            END;
            """
        )
