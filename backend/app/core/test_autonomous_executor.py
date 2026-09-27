from backend.app.core.autonomous_executor import autonomous_executor


task = "Find the official FastAPI documentation."

result = autonomous_executor.execute(
    task_description=task
)

print("\nAutonomous Web Research Result:\n")
print(result)