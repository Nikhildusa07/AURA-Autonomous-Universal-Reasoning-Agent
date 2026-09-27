from backend.app.core.result_generator import result_generator
from backend.app.models.task import Task


goal = "Find the official FastAPI documentation"

task = Task(
    id=1,
    description=goal,
    status="completed",
    priority=1
)

task.complete(
    "All subtasks completed successfully."
)

result = result_generator.generate(
    goal=goal,
    tasks=[task]
)

print("\n========== RESULT GENERATOR TEST ==========")
print("Goal:", result["goal"])
print("Summary:", result["summary"])

print("\n========== TEST RESULT ==========")

if "FastAPI documentation" in result["summary"]:
    print("RESULT FORMAT TEST PASSED")
else:
    print("RESULT FORMAT TEST FAILED")