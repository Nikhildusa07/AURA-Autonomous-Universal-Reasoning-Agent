from backend.app.models.task import Task


class UncertaintyEngine:

    def estimate(self, task: Task) -> dict:
        if task.status == "failed":
            confidence = 0.0
        elif task.status == "completed":
            confidence = 1.0
        else:
            confidence = 0.5

        uncertainty = round(1.0 - confidence, 2)

        return {
            "task_id": task.id,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "status": task.status
        }


uncertainty_engine = UncertaintyEngine()