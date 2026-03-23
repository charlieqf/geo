from __future__ import annotations

from sqlite3 import Connection


class AnswerRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def insert_answer(self, row: tuple[object, ...]) -> None:
        self.connection.execute(
            """
            INSERT INTO answers (
                id, run_id, question_id, prompt_variant, target_provider, target_model,
                answer_text, raw_response_path, extracted_urls_json, latency_ms,
                finish_reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            row,
        )
        self.connection.commit()
