from backend.app.ai.planner import llm_planner


goal = "Build a weather monitoring system using Python and FastAPI."

tasks = llm_planner.create_plan(goal)

print("\nGenerated Plan:\n")

for index, task in enumerate(tasks, start=1):
    print(
        f"{index}. {task['description']} "
        f"(priority: {task['priority']})"
    )