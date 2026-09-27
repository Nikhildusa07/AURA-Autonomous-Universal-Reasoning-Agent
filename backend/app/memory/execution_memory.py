from datetime import datetime
import json
from typing import Any, Optional

from backend.app.memory.database import get_connection


class ExecutionMemory:

    def create_execution(
        self,
        execution_id: str,
        goal: str,
        tasks: Any,
        status: str = "pending"
    ) -> dict:

        connection = get_connection()

        timestamp = datetime.utcnow().isoformat()

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT UNIQUE NOT NULL,
                goal TEXT NOT NULL,
                tasks TEXT NOT NULL,
                status TEXT NOT NULL,
                context TEXT,
                result TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            INSERT INTO execution_memory (
                execution_id,
                goal,
                tasks,
                status,
                context,
                result,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                execution_id,
                goal,
                json.dumps(tasks, default=str),
                status,
                json.dumps({}, default=str),
                json.dumps(None),
                timestamp,
                timestamp
            )
        )

        connection.commit()
        connection.close()

        return self.get_execution(execution_id)

    def get_execution(
        self,
        execution_id: str
    ) -> Optional[dict]:

        connection = get_connection()

        row = connection.execute(
            """
            SELECT
                id,
                execution_id,
                goal,
                tasks,
                status,
                context,
                result,
                created_at,
                updated_at
            FROM execution_memory
            WHERE execution_id = ?
            """,
            (execution_id,)
        ).fetchone()

        connection.close()

        if row is None:
            return None

        return self._serialize(row)

    def update_execution(
        self,
        execution_id: str,
        status: Optional[str] = None,
        context: Any = None,
        result: Any = None,
        tasks: Any = None
    ) -> Optional[dict]:

        existing = self.get_execution(execution_id)

        if existing is None:
            return None

        connection = get_connection()

        updated_status = (
            status
            if status is not None
            else existing["status"]
        )

        updated_context = (
            context
            if context is not None
            else existing["context"]
        )

        updated_result = (
            result
            if result is not None
            else existing["result"]
        )

        updated_tasks = (
            tasks
            if tasks is not None
            else existing["tasks"]
        )

        timestamp = datetime.utcnow().isoformat()

        connection.execute(
            """
            UPDATE execution_memory
            SET
                tasks = ?,
                status = ?,
                context = ?,
                result = ?,
                updated_at = ?
            WHERE execution_id = ?
            """,
            (
                json.dumps(updated_tasks, default=str),
                updated_status,
                json.dumps(updated_context, default=str),
                json.dumps(updated_result, default=str),
                timestamp,
                execution_id
            )
        )

        connection.commit()
        connection.close()

        return self.get_execution(execution_id)

    def update_task(
        self,
        execution_id: str,
        task_id: int,
        task_data: dict
    ) -> Optional[dict]:

        execution = self.get_execution(execution_id)

        if execution is None:
            return None

        tasks = execution["tasks"]

        if not isinstance(tasks, list):
            tasks = []

        updated = False

        for index, task in enumerate(tasks):

            if not isinstance(task, dict):
                continue

            if task.get("id") == task_id:
                tasks[index] = {
                    **task,
                    **task_data
                }
                updated = True
                break

        if not updated:
            tasks.append({
                "id": task_id,
                **task_data
            })

        return self.update_execution(
            execution_id=execution_id,
            tasks=tasks
        )

    def update_context(
        self,
        execution_id: str,
        context: dict
    ) -> Optional[dict]:

        return self.update_execution(
            execution_id=execution_id,
            context=context
        )

    def update_result(
        self,
        execution_id: str,
        result: Any,
        status: Optional[str] = None
    ) -> Optional[dict]:

        return self.update_execution(
            execution_id=execution_id,
            result=result,
            status=status
        )

    def get_pending_executions(self) -> list[dict]:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                id,
                execution_id,
                goal,
                tasks,
                status,
                context,
                result,
                created_at,
                updated_at
            FROM execution_memory
            WHERE status IN ('pending', 'in_progress', 'waiting_for_human')
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        return [
            self._serialize(row)
            for row in rows
        ]

    def get_all_executions(self) -> list[dict]:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                id,
                execution_id,
                goal,
                tasks,
                status,
                context,
                result,
                created_at,
                updated_at
            FROM execution_memory
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        return [
            self._serialize(row)
            for row in rows
        ]

    def delete_execution(
        self,
        execution_id: str
    ) -> bool:

        connection = get_connection()

        cursor = connection.execute(
            """
            DELETE FROM execution_memory
            WHERE execution_id = ?
            """,
            (execution_id,)
        )

        connection.commit()

        deleted = cursor.rowcount > 0

        connection.close()

        return deleted

    def _serialize(self, row) -> dict:

        def parse_json(value, default=None):

            if value is None:
                return default

            try:
                return json.loads(value)
            except (TypeError, json.JSONDecodeError):
                return value

        return {
            "id": row["id"],
            "execution_id": row["execution_id"],
            "goal": row["goal"],
            "tasks": parse_json(
                row["tasks"],
                []
            ),
            "status": row["status"],
            "context": parse_json(
                row["context"],
                {}
            ),
            "result": parse_json(
                row["result"]
            ),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }


execution_memory = ExecutionMemory()