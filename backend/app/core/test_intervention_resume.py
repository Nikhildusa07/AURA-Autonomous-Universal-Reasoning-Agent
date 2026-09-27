from backend.app.core.human_intervention import (
    human_intervention
)
from backend.app.core.intervention_resume import (
    intervention_resume
)


print("\n========== INTERVENTION RESUME TEST ==========")


task_id = 301

task_description = (
    "Calculate 2500 multiplied by 4"
)


# 1. Create a human intervention request
request = human_intervention.request_approval(
    task_id=task_id,
    task_description=task_description,
    reason="Testing resume after human approval."
)

print("\nIntervention Request:")
print(request)


# 2. Try to resume before approval
blocked_result = intervention_resume.resume(
    task_id=task_id,
    task_description=task_description
)

print("\nResume Before Approval:")
print(blocked_result)


# 3. Approve the task
approval_result = human_intervention.respond(
    task_id=task_id,
    response="Approved for execution."
)

print("\nApproval:")
print(approval_result)


# 4. Resume after approval
resume_result = intervention_resume.resume(
    task_id=task_id,
    task_description=task_description
)

print("\nResume After Approval:")
print(resume_result)


print("\n========== TEST RESULT ==========")


blocked_success = (
    blocked_result["success"] is False
    and blocked_result["status"] == "pending"
)


approval_success = (
    approval_result["success"] is True
    and approval_result["status"] == "approved"
)


execution = resume_result.get(
    "execution",
    {}
)

execution_result = execution.get(
    "execution",
    {}
)

tool_result = execution_result.get(
    "result",
    {}
)


resume_success = (
    resume_result["success"] is True
    and resume_result["status"] == "completed"
    and resume_result["human_approval"]["status"]
        == "approved"
    and execution.get("tool") == "calculator"
    and tool_result.get("result") == 10000
)


if (
    blocked_success
    and approval_success
    and resume_success
):
    print(
        "INTERVENTION RESUME TEST PASSED"
    )
else:
    print(
        "INTERVENTION RESUME TEST FAILED"
    )