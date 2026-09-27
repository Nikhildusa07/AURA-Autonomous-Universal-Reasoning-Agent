from datetime import datetime
from typing import Optional

from backend.app.memory.database import get_connection


class InterventionMemory:

    def create_request(
        self,
        task_id: int,
        task_description: str,
        reason: str,
        category: Optional[str] = None,
        execution_id: Optional[str] = None
    ) -> dict:

        connection = get_connection()

        timestamp = datetime.utcnow().isoformat()

        cursor = connection.execute(
            """
            INSERT INTO intervention_requests (
                execution_id,
                task_id,
                task_description,
                reason,
                category,
                status,
                response,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                execution_id,
                task_id,
                task_description,
                reason,
                category,
                "pending",
                None,
                timestamp,
                timestamp
            )
        )

        request_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return self.get_request(request_id)

    def get_request(
        self,
        request_id: int
    ) -> Optional[dict]:

        connection = get_connection()

        row = connection.execute(
            """
            SELECT
                id,
                execution_id,
                task_id,
                task_description,
                reason,
                category,
                status,
                response,
                created_at,
                updated_at
            FROM intervention_requests
            WHERE id = ?
            """,
            (request_id,)
        ).fetchone()

        connection.close()

        if row is None:
            return None

        return self._serialize(row)

    def get_request_by_task_id(
        self,
        task_id: int
    ) -> Optional[dict]:

        connection = get_connection()

        row = connection.execute(
            """
            SELECT
                id,
                execution_id,
                task_id,
                task_description,
                reason,
                category,
                status,
                response,
                created_at,
                updated_at
            FROM intervention_requests
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (task_id,)
        ).fetchone()

        connection.close()

        if row is None:
            return None

        return self._serialize(row)

    def get_request_by_execution_id(
        self,
        execution_id: str
    ) -> Optional[dict]:

        connection = get_connection()

        row = connection.execute(
            """
            SELECT
                id,
                execution_id,
                task_id,
                task_description,
                reason,
                category,
                status,
                response,
                created_at,
                updated_at
            FROM intervention_requests
            WHERE execution_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (execution_id,)
        ).fetchone()

        connection.close()

        if row is None:
            return None

        return self._serialize(row)

    def get_requests_by_execution_id(
        self,
        execution_id: str
    ) -> list[dict]:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                id,
                execution_id,
                task_id,
                task_description,
                reason,
                category,
                status,
                response,
                created_at,
                updated_at
            FROM intervention_requests
            WHERE execution_id = ?
            ORDER BY id ASC
            """,
            (execution_id,)
        ).fetchall()

        connection.close()

        return [
            self._serialize(row)
            for row in rows
        ]

    def get_pending_requests(self) -> list[dict]:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                id,
                execution_id,
                task_id,
                task_description,
                reason,
                category,
                status,
                response,
                created_at,
                updated_at
            FROM intervention_requests
            WHERE status = 'pending'
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        return [
            self._serialize(row)
            for row in rows
        ]

    def get_all_requests(self) -> list[dict]:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                id,
                execution_id,
                task_id,
                task_description,
                reason,
                category,
                status,
                response,
                created_at,
                updated_at
            FROM intervention_requests
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        return [
            self._serialize(row)
            for row in rows
        ]

    def update_status(
        self,
        task_id: int,
        status: str,
        response: Optional[str] = None
    ) -> Optional[dict]:

        connection = get_connection()

        timestamp = datetime.utcnow().isoformat()

        connection.execute(
            """
            UPDATE intervention_requests
            SET status = ?,
                response = ?,
                updated_at = ?
            WHERE task_id = ?
              AND status = 'pending'
            """,
            (
                status,
                response,
                timestamp,
                task_id
            )
        )

        connection.commit()
        connection.close()

        return self.get_request_by_task_id(
            task_id
        )

    def update_status_by_request_id(
        self,
        request_id: int,
        status: str,
        response: Optional[str] = None
    ) -> Optional[dict]:

        connection = get_connection()

        timestamp = datetime.utcnow().isoformat()

        connection.execute(
            """
            UPDATE intervention_requests
            SET status = ?,
                response = ?,
                updated_at = ?
            WHERE id = ?
              AND status = 'pending'
            """,
            (
                status,
                response,
                timestamp,
                request_id
            )
        )

        connection.commit()
        connection.close()

        return self.get_request(
            request_id
        )

    def _serialize(self, row) -> dict:

        return {
            "id": row["id"],
            "execution_id":
                row["execution_id"],
            "task_id":
                row["task_id"],
            "task_description":
                row["task_description"],
            "reason":
                row["reason"],
            "category":
                row["category"],
            "status":
                row["status"],
            "response":
                row["response"],
            "created_at":
                row["created_at"],
            "updated_at":
                row["updated_at"]
        }


intervention_memory = InterventionMemory()