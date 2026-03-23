from __future__ import annotations

from sqlite3 import Connection


class ResultRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def fetch_site_scores(self, run_id: str) -> list[dict[str, object]]:
        rows = self.connection.execute(
            "SELECT * FROM site_scores WHERE run_id = ? ORDER BY final_score DESC",
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]
