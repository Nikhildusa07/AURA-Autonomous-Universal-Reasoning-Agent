from backend.app.api import agent
from backend.app.models.task import Task


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
            description="Deploy AURA to production",
            status="pending",
            priority=1,
            parent_id=1
        )
    )

    return [main_task]


def fake_execute(task_description: str):
    print(
        f"ERROR: Tool execution should not happen "
        f"for intervention task: {task_description}"
    )

    return {
        "success": False,
        "task": task_description,
        "tool": "test_tool",
        "selection_method": "test",
        "error": "Tool execution should have been blocked."
    }


original_create_plan = agent.planner.create_plan
original_execute = agent.autonomous_executor.execute

try:
    agent.planner.create_plan = fake_plan
    agent.autonomous_executor.execute = fake_execute

    response = agent.run_agent(
        agent.AgentRequest(
            goal="Test human intervention integration"
        )
    )

finally:
    agent.planner.create_plan = original_create_plan
    agent.autonomous_executor.execute = original_execute


print("\n========== AURA HUMAN INTERVENTION INTEGRATION TEST ==========")

print("\nOverall status:")
print(response["status"])

print("\nPlan:")
print(response["plan"])

print("\nHuman intervention:")
print(response["human_intervention"])

print("\nTool outputs:")
print(
    response["context"]["data"]["tool_outputs"]
)

print("\nTrace events:")

for event in response["execution_trace"]:
    if (
        "intervention" in event["event"]
        or "execution" in event["event"]
    ):
        print(
            event["event"],
            "->",
            event["details"]
        )


print("\n========== TEST RESULT ==========")


subtask = response["plan"][0]["subtasks"][0]

intervention = response[
    "human_intervention"
]

tool_outputs = response[
    "context"
]["data"]["tool_outputs"]

trace_event_names = [
    event["event"]
    for event in response["execution_trace"]
]


test_passed = (
    response["status"] == "waiting_for_human"
    and subtask["status"] == "pending"
    and intervention["required"] is True
    and intervention["count"] == 1
    and len(intervention["requests"]) == 1
    and len(tool_outputs) == 0
    and "human_intervention_required"
    in trace_event_names
    and "intervention_check"
    in trace_event_names
    and "tool_execution_completed"
    not in trace_event_names
)


if test_passed:
    print(
        "AURA HUMAN INTERVENTION INTEGRATION TEST PASSED"
    )
else:
    print(
        "AURA HUMAN INTERVENTION INTEGRATION TEST FAILED"
    )