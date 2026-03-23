from __future__ import annotations

from sqlite3 import Connection


class PromptRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def insert_snapshot(
        self,
        snapshot_id: str,
        run_id: str,
        prompt_group: str,
        prompt_name: str,
        version_label: str,
        system_prompt: str | None,
        user_template: str,
        parameters_json: str,
        created_at: str,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO prompt_snapshots (
                id, run_id, prompt_group, prompt_name, version_label,
                system_prompt, user_template, parameters_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                run_id,
                prompt_group,
                prompt_name,
                version_label,
                system_prompt,
                user_template,
                parameters_json,
                created_at,
            ),
        )
        self.connection.commit()
