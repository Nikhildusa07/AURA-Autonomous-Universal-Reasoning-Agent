from typing import Any


class GoalPrioritizer:
    """
    Determines execution priority for goals and tasks.

    Priority scale:
        10 = Critical
         8 = Very High
         6 = High
         4 = Normal
         2 = Low
         1 = Very Low
    """

    PRIORITY_KEYWORDS = {
        10: [
            "critical",
            "urgent",
            "emergency",
            "immediately",
            "as soon as possible",
        ],
        8: [
            "important",
            "high priority",
            "must",
            "required",
            "deadline",
        ],
        6: [
            "priority",
            "important task",
            "need to",
            "should",
        ],
        4: [
            "analyze",
            "research",
            "build",
            "create",
            "develop",
            "prepare",
        ],
        2: [
            "optional",
            "later",
            "nice to have",
            "improvement",
        ],
    }

    def calculate_priority(
        self,
        description: str,
        explicit_priority: int | None = None,
    ) -> int:
        """
        Calculate the priority of a goal/task.
        """

        if explicit_priority is not None:
            return self.normalize_priority(
                explicit_priority
            )

        text = (description or "").strip().lower()

        if not text:
            return 1

        for priority in sorted(
            self.PRIORITY_KEYWORDS.keys(),
            reverse=True,
        ):
            keywords = self.PRIORITY_KEYWORDS[priority]

            if any(
                keyword in text
                for keyword in keywords
            ):
                return priority

        return 4

    def normalize_priority(
        self,
        priority: int,
    ) -> int:
        """
        Convert any priority value into the supported
        1-10 range.
        """

        try:
            priority = int(priority)
        except (TypeError, ValueError):
            return 4

        return max(
            1,
            min(10, priority)
        )

    def prioritize_tasks(
        self,
        tasks: list[Any],
    ) -> list[Any]:
        """
        Calculate and assign priorities, then sort tasks
        from highest priority to lowest priority.

        Stable ordering is preserved when priorities match.
        """

        prioritized = []

        for index, task in enumerate(tasks):
            description = getattr(
                task,
                "description",
                "",
            )

            current_priority = getattr(
                task,
                "priority",
                None,
            )

            priority = self.calculate_priority(
                description=description,
                explicit_priority=current_priority,
            )

            task.priority = priority

            prioritized.append(
                (
                    priority,
                    index,
                    task,
                )
            )

        prioritized.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        return [
            item[2]
            for item in prioritized
        ]

    def prioritize_plan(
        self,
        plan: list[Any],
    ) -> list[Any]:
        """
        Prioritize top-level tasks and their subtasks.
        """

        prioritized_plan = self.prioritize_tasks(
            plan
        )

        for task in prioritized_plan:
            subtasks = getattr(
                task,
                "subtasks",
                [],
            )

            if subtasks:
                task.subtasks = self.prioritize_tasks(
                    subtasks
                )

        return prioritized_plan

    def get_priority_label(
        self,
        priority: int,
    ) -> str:
        priority = self.normalize_priority(
            priority
        )

        if priority >= 10:
            return "critical"

        if priority >= 8:
            return "very_high"

        if priority >= 6:
            return "high"

        if priority >= 4:
            return "normal"

        if priority >= 2:
            return "low"

        return "very_low"

    def get_priority_metadata(
        self,
        task: Any,
    ) -> dict:
        priority = self.normalize_priority(
            getattr(task, "priority", 1)
        )

        return {
            "task_id": getattr(
                task,
                "id",
                None,
            ),
            "description": getattr(
                task,
                "description",
                "",
            ),
            "priority": priority,
            "priority_label": self.get_priority_label(
                priority
            ),
        }


goal_prioritizer = GoalPrioritizer()