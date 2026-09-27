from backend.app.models.task import Task


class Evaluator:

    def evaluate_task(self, task: Task) -> dict:
        if task.status == "failed":
            return {
                "success": False,
                "task_id": task.id,
                "status": "failed",
                "reason": task.error
            }

        if task.subtasks:
            failed_subtasks = [
                subtask
                for subtask in task.subtasks
                if subtask.status == "failed"
            ]

            if failed_subtasks:
                return {
                    "success": False,
                    "task_id": task.id,
                    "status": "failed",
                    "reason": "One or more subtasks failed."
                }

        if task.status == "completed":
            return {
                "success": True,
                "task_id": task.id,
                "status": "completed",
                "reason": "Task completed successfully."
            }

        return {
            "success": False,
            "task_id": task.id,
            "status": task.status,
            "reason": "Task has not been completed."
        }


evaluator = Evaluator()