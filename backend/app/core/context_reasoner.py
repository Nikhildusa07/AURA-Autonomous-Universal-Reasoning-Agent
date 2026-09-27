from typing import Any


class ContextReasoner:

    def reason(
        self,
        task_description: str,
        context: dict[str, Any] | None = None
    ) -> dict:

        description = task_description.strip()

        if not description:
            return {
                "success": False,
                "task": task_description,
                "error": "Task description cannot be empty."
            }

        context = context or {}

        completed_tasks = context.get(
            "completed_task_results",
            []
        )

        relevant_results = []

        for task in completed_tasks:
            if not isinstance(task, dict):
                continue

            if task.get("success") is not True:
                continue

            relevant_results.append({
                "task_id": task.get("task_id"),
                "task_description":
                    task.get("task_description"),
                "result": task.get("result")
            })

        return {
            "success": True,
            "task": description,
            "reasoning_type": "context_aware",
            "context_used": len(relevant_results) > 0,
            "previous_results": relevant_results,
            "analysis": {
                "message": (
                    "The task was analyzed using "
                    "results from previously completed tasks."
                ),
                "previous_task_count":
                    len(relevant_results)
            }
        }


context_reasoner = ContextReasoner()