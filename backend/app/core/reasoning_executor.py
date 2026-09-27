from typing import Any

from backend.app.core.context_reasoner import context_reasoner


class ReasoningExecutor:

    def execute(
        self,
        task_description: str,
        context: dict[str, Any] | None = None
    ) -> dict:

        description = task_description.strip()

        if not description:
            return {
                "success": False,
                "task": task_description,
                "execution_type": "reasoning",
                "result": None,
                "error": "Task description cannot be empty."
            }

        context = context or {}

        reasoning_result = context_reasoner.reason(
            task_description=description,
            context=context
        )

        if not reasoning_result["success"]:
            return {
                "success": False,
                "task": description,
                "execution_type": "reasoning",
                "result": reasoning_result,
                "error": reasoning_result.get(
                    "error",
                    "Reasoning failed."
                )
            }

        return {
            "success": True,
            "task": description,
            "execution_type": "reasoning",
            "result": reasoning_result
        }


reasoning_executor = ReasoningExecutor()