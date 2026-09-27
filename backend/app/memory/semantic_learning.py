from __future__ import annotations

import re
from typing import Any, Optional

from backend.app.memory.memory import memory


class SemanticLearning:

    def __init__(self):
        self.memory = memory

    def learn(
        self,
        key: str,
        value: Any,
    ) -> dict:
        """
        Store a reusable semantic fact.

        Existing facts with the same key are updated.
        """

        normalized_key = self._normalize_key(key)

        if not normalized_key:
            raise ValueError("Semantic memory key cannot be empty.")

        self.memory.remember_fact(
            normalized_key,
            value,
        )

        return {
            "success": True,
            "key": normalized_key,
            "value": value,
        }

    def learn_from_execution(
        self,
        goal: str,
        tasks: list[Any],
        status: str = "completed",
    ) -> dict:
        """
        Extract reusable facts from an agent execution
        and store them in semantic memory.
        """

        goal = (goal or "").strip()

        if not goal:
            return {
                "success": False,
                "learned": 0,
                "facts": [],
                "error": "Goal cannot be empty.",
            }

        learned_facts: list[dict] = []

        # ---------------------------------------------------------
        # 1. Remember the latest successfully completed goal
        # ---------------------------------------------------------

        self.learn(
            "last_goal",
            {
                "goal": goal,
                "status": status,
            },
        )

        learned_facts.append(
            {
                "key": "last_goal",
                "value": goal,
            }
        )

        # ---------------------------------------------------------
        # 2. Store the result of the completed goal
        # ---------------------------------------------------------

        completed_tasks = [
            task
            for task in tasks
            if getattr(task, "status", None) == "completed"
        ]

        if completed_tasks:
            task_results = []

            for task in completed_tasks:
                result = getattr(task, "result", None)

                if result is None:
                    continue

                task_results.append(
                    {
                        "task_id": getattr(task, "id", None),
                        "description": getattr(
                            task,
                            "description",
                            "",
                        ),
                        "result": result,
                    }
                )

            if task_results:
                goal_key = self._create_goal_key(goal)

                self.learn(
                    goal_key,
                    {
                        "goal": goal,
                        "status": status,
                        "results": task_results,
                    },
                )

                learned_facts.append(
                    {
                        "key": goal_key,
                        "value": {
                            "goal": goal,
                            "status": status,
                            "results": task_results,
                        },
                    }
                )

        # ---------------------------------------------------------
        # 3. Learn useful tool usage
        # ---------------------------------------------------------

        for task in completed_tasks:

            result = getattr(task, "result", None)

            if not isinstance(result, dict):
                continue

            tool_name = result.get("tool")

            if not tool_name:
                continue

            tool_key = f"tool_success:{self._normalize_key(tool_name)}"

            existing = self.memory.get_fact(tool_key)

            execution_count = 0

            if isinstance(existing, dict):
                execution_count = int(
                    existing.get("execution_count", 0)
                )

            execution_count += 1

            tool_fact = {
                "tool": tool_name,
                "execution_count": execution_count,
                "last_goal": goal,
                "last_status": status,
            }

            self.learn(
                tool_key,
                tool_fact,
            )

            learned_facts.append(
                {
                    "key": tool_key,
                    "value": tool_fact,
                }
            )

        # ---------------------------------------------------------
        # 4. Learn successful calculation results
        # ---------------------------------------------------------

        for task in completed_tasks:

            result = getattr(task, "result", None)

            if not isinstance(result, dict):
                continue

            if result.get("tool") != "calculator":
                continue

            expression = result.get("expression")
            calculation_result = result.get("result")

            if expression is None or calculation_result is None:
                continue

            calculation_key = (
                f"calculation:{self._normalize_key(str(expression))}"
            )

            calculation_fact = {
                "expression": expression,
                "result": calculation_result,
                "goal": goal,
            }

            self.learn(
                calculation_key,
                calculation_fact,
            )

            learned_facts.append(
                {
                    "key": calculation_key,
                    "value": calculation_fact,
                }
            )

        # ---------------------------------------------------------
        # 5. Learn successful research results
        # ---------------------------------------------------------

        for task in completed_tasks:

            result = getattr(task, "result", None)

            if not isinstance(result, dict):
                continue

            if result.get("tool") != "web_research":
                continue

            query = result.get("query")

            if not query:
                continue

            research_key = (
                f"research:{self._normalize_key(str(query))}"
            )

            research_fact = {
                "query": query,
                "count": result.get("count", 0),
                "results": result.get("results", []),
                "goal": goal,
            }

            self.learn(
                research_key,
                research_fact,
            )

            learned_facts.append(
                {
                    "key": research_key,
                    "value": research_fact,
                }
            )

        return {
            "success": True,
            "learned": len(learned_facts),
            "facts": learned_facts,
        }

    def recall(
        self,
        key: str,
    ) -> Optional[Any]:
        """
        Retrieve one semantic fact.
        """

        normalized_key = self._normalize_key(key)

        if not normalized_key:
            return None

        return self.memory.get_fact(
            normalized_key
        )

    def recall_all(self) -> dict:
        """
        Retrieve all semantic knowledge.
        """

        return self.memory.get_all_facts()

    def _create_goal_key(
        self,
        goal: str,
    ) -> str:
        normalized = self._normalize_key(goal)

        return f"goal:{normalized[:180]}"

    def _normalize_key(
        self,
        value: str,
    ) -> str:
        value = str(value or "").strip().lower()

        value = re.sub(
            r"\s+",
            "_",
            value,
        )

        value = re.sub(
            r"[^a-z0-9_\-:.]",
            "",
            value,
        )

        value = re.sub(
            r"_+",
            "_",
            value,
        )

        return value.strip("_")


semantic_learning = SemanticLearning()