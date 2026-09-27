from typing import Any

from backend.app.core.autonomous_executor import autonomous_executor
from backend.app.core.task_context import task_context


class ContextAwareExecutor:

    def __init__(self):
        self.executor = autonomous_executor
        self.context = task_context

    def execute(
        self,
        task_id: int,
        task_description: str
    ) -> dict:

        description = task_description.strip()

        if not description:
            return {
                "success": False,
                "task_id": task_id,
                "task": task_description,
                "error": "Task description cannot be empty."
            }

        previous_context = self.context.build_context(
            exclude_task_id=task_id
        )

        execution_result = self.executor.execute(
            task_description=description,
            context=previous_context
        )

        success = execution_result.get(
            "success",
            False
        )

        stored_context = self.context.store(
            task_id=task_id,
            task_description=description,
            result=execution_result,
            success=success
        )

        return {
            "success": success,
            "task_id": task_id,
            "task": description,
            "context_used": previous_context,
            "execution": execution_result,
            "stored_result": stored_context
        }

    def get_context(self) -> dict:
        return self.context.build_context()

    def get_task_result(
        self,
        task_id: int
    ) -> Any:
        return self.context.get_result(task_id)

    def clear_context(self):
        self.context.clear()


context_aware_executor = ContextAwareExecutor()