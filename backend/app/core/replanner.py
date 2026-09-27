from backend.app.models.task import Task


class Replanner:

    def create_recovery_plan(self, task: Task) -> dict:
        return {
            "task_id": task.id,
            "original_task": task.description,
            "action": "retry",
            "reason": task.error or "Task requires replanning.",
            "new_plan": [
                "Analyze the failure",
                "Identify an alternative approach",
                "Retry the task",
                "Evaluate the new result"
            ]
        }


replanner = Replanner()