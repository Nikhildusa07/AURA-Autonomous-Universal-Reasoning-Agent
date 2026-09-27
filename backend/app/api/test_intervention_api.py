from backend.app.api.intervention import (
    get_pending_interventions,
    get_all_interventions,
    approve_intervention,
    reject_intervention,
    resume_intervention,
    InterventionResponse,
    InterventionResumeRequest,
)
from backend.app.core.human_intervention import (
    human_intervention
)


print("\n========== INTERVENTION API TEST ==========")


# Create a test intervention request directly.
task_id = 401
task_description = "Calculate 5000 multiplied by 2"

human_intervention.request_approval(
    task_id=task_id,
    task_description=task_description,
    reason="Testing intervention API."
)


# 1. GET pending interventions
pending_result = get_pending_interventions()

print("\nPending:")
print(pending_result)


# 2. Approve intervention
approval_result = approve_intervention(
    task_id=task_id,
    request=InterventionResponse(
        response="Approved through API."
    )
)

print("\nApproval:")
print(approval_result)


# 3. Resume the approved task
resume_result = resume_intervention(
    request=InterventionResumeRequest(
        task_id=task_id,
        task_description=task_description
    )
)

print("\nResume:")
print(resume_result)


# 4. Create another intervention for rejection
rejection_task_id = 402

human_intervention.request_approval(
    task_id=rejection_task_id,
    task_description="Delete production database",
    reason="Testing API rejection."
)


# 5. Reject intervention
rejection_result = reject_intervention(
    task_id=rejection_task_id,
    request=InterventionResponse(
        response="Rejected through API."
    )
)

print("\nRejection:")
print(rejection_result)


# 6. Get all interventions
all_result = get_all_interventions()

print("\nAll Interventions:")
print(all_result)


print("\n========== TEST RESULT ==========")


pending_success = (
    pending_result["success"] is True
    and any(
        item["task_id"] == task_id
        for item in pending_result["requests"]
    )
)


approval_success = (
    approval_result["success"] is True
    and approval_result["status"] == "approved"
)


resume_execution = resume_result.get(
    "execution",
    {}
)

resume_tool_result = (
    resume_execution
    .get("execution", {})
    .get("result", {})
)


resume_success = (
    resume_result["success"] is True
    and resume_result["status"] == "completed"
    and resume_execution["tool"] == "calculator"
    and resume_tool_result["result"] == 10000
)


rejection_success = (
    rejection_result["success"] is True
    and rejection_result["status"] == "rejected"
)


all_success = (
    all_result["success"] is True
    and all_result["count"] >= 2
)


if (
    pending_success
    and approval_success
    and resume_success
    and rejection_success
    and all_success
):
    print(
        "INTERVENTION API TEST PASSED"
    )
else:
    print(
        "INTERVENTION API TEST FAILED"
    )