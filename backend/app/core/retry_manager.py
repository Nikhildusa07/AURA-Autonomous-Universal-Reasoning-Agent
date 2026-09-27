from backend.app.models.task import Task


class RetryManager:

    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self.retry_counts: dict[int, int] = {}

    def can_retry(self, task: Task) -> bool:
        retry_count = self.retry_counts.get(task.id, 0)

        return retry_count < self.max_retries

    def prepare_retry(self, task: Task) -> dict:
        retry_count = self.retry_counts.get(task.id, 0)

        if retry_count >= self.max_retries:
            return {
                "retry": False,
                "task_id": task.id,
                "retry_count": retry_count,
                "max_retries": self.max_retries,
                "message": "Maximum retry limit reached."
            }

        retry_count += 1

        self.retry_counts[task.id] = retry_count

        previous_error = task.error

        task.status = "pending"
        task.result = None
        task.error = None

        return {
            "retry": True,
            "task_id": task.id,
            "retry_count": retry_count,
            "max_retries": self.max_retries,
            "previous_error": previous_error,
            "message": "Task prepared for retry."
        }

    def reset(self):
        self.retry_counts.clear()


retry_manager = RetryManager()