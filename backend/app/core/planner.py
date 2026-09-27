from backend.app.models.task import Task
from backend.app.ai.planner import llm_planner


class Planner:

    def create_plan(self, goal: str) -> list[Task]:
        goal = goal.strip()

        if not goal:
            return []

        generated_tasks = llm_planner.create_plan(goal)

        main_task = Task(
            id=1,
            description=goal,
            status="pending",
            priority=1
        )

        for index, task_data in enumerate(
            generated_tasks,
            start=2
        ):
            subtask = Task(
                id=index,
                description=task_data["description"],
                priority=task_data["priority"],
                parent_id=1
            )

            main_task.add_subtask(subtask)

        return [main_task]