from backend.app.core.retry_manager import RetryManager
from backend.app.models.task import Task


retry_manager = RetryManager(max_retries=2)

task = Task(
    id=1,
    description="Test retry behavior"
)

task.fail("Simulated execution failure.")

print("\nInitial Task:")
print({
    "status": task.status,
    "error": task.error
})

print("\nRetry 1:")
result_1 = retry_manager.prepare_retry(task)
print(result_1)
print({
    "status": task.status,
    "error": task.error,
    "result": task.result
})

task.fail("Simulated second failure.")

print("\nRetry 2:")
result_2 = retry_manager.prepare_retry(task)
print(result_2)
print({
    "status": task.status,
    "error": task.error,
    "result": task.result
})

task.fail("Simulated third failure.")

print("\nRetry 3:")
result_3 = retry_manager.prepare_retry(task)
print(result_3)
print({
    "status": task.status,
    "error": task.error
})