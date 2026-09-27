from backend.app.models.task import Task


class RecoveryEngine:

    def recover(self, task: Task) -> dict:
        if task.status != "failed":
            return {
                "recovered": False,
                "task_id": task.id,
                "message": "No recovery required."
            }

        task.status = "pending"
        task.error = None

        return {
            "recovered": True,
            "task_id": task.id,
            "status": task.status,
            "message": "Task reset for re-execution."
        }


recovery_engine = RecoveryEngine()