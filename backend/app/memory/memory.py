from datetime import datetime
import json
from typing import Any

from backend.app.memory.database import get_connection


class Memory:

    def remember_episode(
        self,
        goal: str,
        result: Any,
        status: str
    ):
        connection = get_connection()

        connection.execute(
            """
            INSERT INTO episodic_memory
            (timestamp, goal, result, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                goal,
                json.dumps(result, default=str),
                status
            )
        )

        connection.commit()
        connection.close()

    def remember_fact(self, key: str, value: Any):
        connection = get_connection()

        connection.execute(
            """
            INSERT INTO semantic_memory
            (memory_key, memory_value, timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(memory_key)
            DO UPDATE SET
                memory_value = excluded.memory_value,
                timestamp = excluded.timestamp
            """,
            (
                key,
                json.dumps(value, default=str),
                datetime.utcnow().isoformat()
            )
        )

        connection.commit()
        connection.close()

    def get_episodes(self):
        connection = get_connection()

        rows = connection.execute(
            """
            SELECT id, timestamp, goal, result, status
            FROM episodic_memory
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        episodes = []

        for row in rows:
            episodes.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "goal": row["goal"],
                "result": json.loads(row["result"]),
                "status": row["status"]
            })

        return episodes

    def get_fact(self, key: str):
        connection = get_connection()

        row = connection.execute(
            """
            SELECT memory_value
            FROM semantic_memory
            WHERE memory_key = ?
            """,
            (key,)
        ).fetchone()

        connection.close()

        if row is None:
            return None

        return json.loads(row["memory_value"])

    def get_all_facts(self):
        connection = get_connection()

        rows = connection.execute(
            """
            SELECT memory_key, memory_value, timestamp
            FROM semantic_memory
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        facts = {}

        for row in rows:
            facts[row["memory_key"]] = {
                "value": json.loads(row["memory_value"]),
                "timestamp": row["timestamp"]
            }

        return facts


memory = Memory()