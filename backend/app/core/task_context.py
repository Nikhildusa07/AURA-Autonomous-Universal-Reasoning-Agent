from typing import Any


class TaskContext:

    def __init__(self):
        self._data: dict[int, dict[str, Any]] = {}

    def store(
        self,
        task_id: int,
        task_description: str,
        result: Any,
        success: bool = True
    ) -> dict:

        self._data[task_id] = {
            "task_id": task_id,
            "task_description": task_description,
            "result": result,
            "success": success
        }

        return self._data[task_id]

    def get(
        self,
        task_id: int
    ) -> dict | None:

        return self._data.get(task_id)

    def get_result(
        self,
        task_id: int
    ) -> Any:

        task = self.get(task_id)

        if task is None:
            return None

        return task.get("result")

    def get_all(self) -> list[dict]:

        return list(
            self._data.values()
        )

    def get_successful_results(self) -> list[dict]:

        return [
            item
            for item in self._data.values()
            if item.get("success") is True
        ]

    def get_failed_results(self) -> list[dict]:

        return [
            item
            for item in self._data.values()
            if item.get("success") is False
        ]

    def build_context(
        self,
        exclude_task_id: int | None = None
    ) -> dict:

        tasks = []

        for item in self._data.values():

            if (
                exclude_task_id is not None
                and item["task_id"] == exclude_task_id
            ):
                continue

            tasks.append(item)

        return {
            "completed_task_results": tasks,
            "task_count": len(tasks)
        }

    def clear(self):
        self._data.clear()


task_context = TaskContext()