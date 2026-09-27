from backend.app.api import agent
from backend.app.models.task import Task


execution_calls = {
    "count": 0
}


def fake_plan(goal: str):
    main_task = Task(
        id=1,
        description=goal,
        status="pending",
        priority=1
    )

    main_task.add_subtask(
        Task(
            id=2,
            description="Simulated flaky task",
            status="pending",
            priority=1,
            parent_id=1
        )
    )

    return [main_task]


def fake_execute(task_description: str):
    execution_calls["count"] += 1

    attempt = execution_calls["count"]

    if attempt == 1:
        return {
            "success": False,
            "task": task_description,
            "tool": "test_tool",
            "selection_method": "test",
            "error": "Simulated temporary failure."
        }

    return {
        "success": True,
        "task": task_description,
        "tool": "test_tool",
        "selection_method": "test",
        "arguments": {},
        "execution": {
            "success": True,
            "tool": "test_tool",
            "result": {
                "message": "Task succeeded after retry."
            }
        }
    }


original_create_plan = agent.planner.create_plan
original_execute = agent.autonomous_executor.execute

try:
    agent.planner.create_plan = fake_plan
    agent.autonomous_executor.execute = fake_execute

    response = agent.run_agent(
        agent.AgentRequest(
            goal="Test AURA retry mechanism"
        )
    )

finally:
    agent.planner.create_plan = original_create_plan
    agent.autonomous_executor.execute = original_execute


print("\n========== AURA RETRY TEST ==========")

print(
    "Execution attempts:",
    execution_calls["count"]
)

print(
    "Overall status:",
    response["status"]
)

print(
    "Plan:",
    response["plan"]
)

print("\nRetry events:")

retry_events = [
    event
    for event in response["execution_trace"]
    if "retry" in event["event"]
]

for event in retry_events:
    print(
        event["event"],
        "->",
        event["details"]
    )


print("\nTool outputs:")

tool_outputs = response["context"]["data"]["tool_outputs"]

print(
    "Tool output count:",
    len(tool_outputs)
)

print(
    tool_outputs
)


print("\n========== TEST RESULT ==========")

subtask = response["plan"][0]["subtasks"][0]

retry_event_names = [
    event["event"]
    for event in response["execution_trace"]
]


retry_worked = (
    execution_calls["count"] == 2
    and subtask["status"] == "completed"
    and response["status"] == "completed"
    and len(tool_outputs) == 2
    and "retry_attempted" in retry_event_names
    and "subtask_retry_started" in retry_event_names
    and "subtask_retry_completed" in retry_event_names
    and "tool_execution_completed" in retry_event_names
)


if retry_worked:
    print(
        "AURA RETRY + CONTEXT INTEGRATION TEST PASSED"
    )
else:
    print(
        "AURA RETRY + CONTEXT INTEGRATION TEST FAILED"
    )