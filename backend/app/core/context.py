from copy import deepcopy
from typing import Any


class ContextManager:

    def __init__(self):
        self.reset()

    def reset(self):
        self.context = {
            "goal": None,
            "tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "tool_outputs": [],
            "evaluations": [],
            "reflections": [],
            "verifications": [],
            "memory": [],
        }

    # =========================================================
    # GOAL
    # =========================================================

    def set_goal(self, goal: str):
        self.context["goal"] = goal

    # =========================================================
    # TASK MANAGEMENT
    # =========================================================

    def add_task(self, task: dict):
        self.context["tasks"].append(
            deepcopy(task)
        )

    def update_task(
        self,
        task_id: int,
        task: dict
    ):
        """
        Update an existing task in the main context.

        This keeps the context task state synchronized
        with the actual execution state.
        """

        updated = False

        for index, existing_task in enumerate(
            self.context["tasks"]
        ):

            if existing_task.get("id") == task_id:

                self.context["tasks"][index] = (
                    deepcopy(task)
                )

                updated = True
                break

        if not updated:
            self.context["tasks"].append(
                deepcopy(task)
            )

        return {
            "success": True,
            "task_id": task_id,
            "updated": updated
        }

    def add_completed_task(self, task: dict):
        """
        Store the latest completed version of a task.
        """

        self._upsert_context_list(
            "completed_tasks",
            task
        )

        self.update_task(
            task_id=task["id"],
            task=task
        )

    def add_failed_task(self, task: dict):
        """
        Store the latest failed version of a task.
        """

        self._upsert_context_list(
            "failed_tasks",
            task
        )

        self.update_task(
            task_id=task["id"],
            task=task
        )

    # =========================================================
    # TOOL OUTPUTS
    # =========================================================

    def add_tool_output(self, output: Any):
        self.context["tool_outputs"].append(
            deepcopy(output)
        )

    # =========================================================
    # EVALUATION
    # =========================================================

    def add_evaluation(self, evaluation: dict):
        self.context["evaluations"].append(
            deepcopy(evaluation)
        )

    # =========================================================
    # REFLECTION
    # =========================================================

    def add_reflection(self, reflection: dict):
        self.context["reflections"].append(
            deepcopy(reflection)
        )

    # =========================================================
    # VERIFICATION
    # =========================================================

    def add_verification(self, verification: dict):
        self.context["verifications"].append(
            deepcopy(verification)
        )

    # =========================================================
    # MEMORY
    # =========================================================

    def add_memory(self, memory: Any):
        self.context["memory"].append(
            deepcopy(memory)
        )

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================

    def _upsert_context_list(
        self,
        list_name: str,
        task: dict
    ):
        """
        Insert a task if it does not exist.
        Otherwise replace the previous version.
        """

        task_id = task.get("id")

        target_list = self.context[list_name]

        for index, existing_task in enumerate(
            target_list
        ):

            if existing_task.get("id") == task_id:

                target_list[index] = deepcopy(task)

                return

        target_list.append(
            deepcopy(task)
        )

    # =========================================================
    # CONTEXT ACCESS
    # =========================================================

    def get_context(self):
        """
        Return a deep copy so external code cannot
        accidentally modify the internal context.
        """

        return deepcopy(
            self.context
        )

    def get_summary(self):
        return {
            "goal": self.context["goal"],
            "total_tasks": len(
                self.context["tasks"]
            ),
            "completed_tasks": len(
                self.context["completed_tasks"]
            ),
            "failed_tasks": len(
                self.context["failed_tasks"]
            ),
            "tool_outputs": len(
                self.context["tool_outputs"]
            ),
            "evaluations": len(
                self.context["evaluations"]
            ),
            "reflections": len(
                self.context["reflections"]
            ),
            "verifications": len(
                self.context["verifications"]
            ),
            "memory_items": len(
                self.context["memory"]
            ),
        }


context_manager = ContextManager()