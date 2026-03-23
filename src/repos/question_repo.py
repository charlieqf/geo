from __future__ import annotations

from sqlite3 import Connection


class QuestionRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def insert_many(
        self, rows: list[tuple[str, str, int, str, str, str | None, str]]
    ) -> None:
        self.connection.executemany(
            """
            INSERT INTO questions (
                id, run_id, display_order, intent_bucket, question_text,
                why_this_question, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.connection.commit()
