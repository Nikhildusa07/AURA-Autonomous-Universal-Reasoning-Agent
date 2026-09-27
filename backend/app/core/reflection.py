from backend.app.models.task import Task


class ReflectionEngine:

    def reflect(self, task: Task) -> dict:
        if task.status == "completed":
            assessment = "Task completed successfully."
            recommendation = "Continue with the next task or finalize the result."
        elif task.status == "failed":
            assessment = "Task execution failed."
            recommendation = "Analyze the failure and attempt an alternative approach."
        elif task.status == "in_progress":
            assessment = "Task is currently being executed."
            recommendation = "Continue execution and evaluate the result."
        else:
            assessment = "Task has not been executed yet."
            recommendation = "Execute the task before evaluating the result."

        return {
            "task_id": task.id,
            "status": task.status,
            "assessment": assessment,
            "recommendation": recommendation,
            "result": task.result,
            "error": task.error
        }


reflection_engine = ReflectionEngine()