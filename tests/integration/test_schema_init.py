import sqlite3
from pathlib import Path

from src.db import init_db


def test_init_db_creates_core_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "geo.sqlite3"

    init_db(db_path)

    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    finally:
        connection.close()

    table_names = {row[0] for row in rows}

    assert {
        "runs",
        "prompt_snapshots",
        "questions",
        "answers",
        "answer_sources",
        "answer_topic_units",
        "normalized_topics",
        "topic_memberships",
        "site_topic_support",
        "site_scores",
        "golden_set_items",
    }.issubset(table_names)


def test_init_db_adds_platform_classification_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "geo.sqlite3"

    init_db(db_path)

    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute("PRAGMA table_info(answer_sources)").fetchall()
    finally:
        connection.close()

    column_names = {row[1] for row in rows}

    assert {
        "source_label",
        "source_role",
        "normalized_platform",
        "is_actionable_platform",
    }.issubset(column_names)


def test_init_db_adds_answer_preprocess_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "geo.sqlite3"

    init_db(db_path)

    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute("PRAGMA table_info(answer_topic_units)").fetchall()
    finally:
        connection.close()

    column_names = {row[1] for row in rows}

    assert {
        "interpretation_label",
        "brand_grounded",
        "source_explicitness_score",
    }.issubset(column_names)
