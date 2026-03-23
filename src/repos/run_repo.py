from __future__ import annotations

from dataclasses import dataclass
from sqlite3 import Connection


@dataclass(slots=True)
class RunRecord:
    id: str
    keyword_input: str
    status: str
    target_provider: str
    target_model: str
    analysis_provider: str
    analysis_model: str
    question_count: int
    created_at: str


class RunRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def insert(self, record: RunRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO runs (
                id, keyword_input, brand_name, region, target_provider, target_model,
                analysis_provider, analysis_model, target_coverage, question_count,
                status, notes, created_at, completed_at
            ) VALUES (?, ?, NULL, NULL, ?, ?, ?, ?, 0.85, ?, ?, NULL, ?, NULL)
            """,
            (
                record.id,
                record.keyword_input,
                record.target_provider,
                record.target_model,
                record.analysis_provider,
                record.analysis_model,
                record.question_count,
                record.status,
                record.created_at,
            ),
        )
        self.connection.commit()
