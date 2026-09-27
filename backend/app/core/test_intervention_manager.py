from backend.app.core.intervention_manager import (
    intervention_manager
)


print("\n========== INTERVENTION MANAGER TEST ==========")


# Test 1: Normal task should not require intervention
normal_task = intervention_manager.check_task(
    task_id=201,
    task_description="Calculate 100 multiplied by 25"
)

print("\nNormal Task:")
print(normal_task)


# Test 2: Production task should require intervention
production_task = intervention_manager.check_task(
    task_id=202,
    task_description="Deploy AURA to production"
)

print("\nProduction Task:")
print(production_task)


# Test 3: Check pending requests
pending_requests = intervention_manager.get_pending()

print("\nPending Requests:")
print(pending_requests)


# Test 4: Approve production task
approval_result = intervention_manager.approve(
    task_id=202,
    response="Approved for deployment."
)

print("\nApproval Result:")
print(approval_result)


# Test 5: Check pending requests after approval
pending_after_approval = (
    intervention_manager.get_pending()
)

print("\nPending After Approval:")
print(pending_after_approval)


# Test 6: Destructive task
destructive_task = intervention_manager.check_task(
    task_id=203,
    task_description="Delete the production database"
)

print("\nDestructive Task:")
print(destructive_task)


# Test 7: Reject destructive task
rejection_result = intervention_manager.reject(
    task_id=203,
    response="Rejected. Do not delete the database."
)

print("\nRejection Result:")
print(rejection_result)


print("\n========== TEST RESULT ==========")


normal_success = (
    normal_task["required"] is False
    and normal_task["status"] == "not_required"
)


production_success = (
    production_task["required"] is True
    and production_task["status"] == "pending"
    and production_task["category"] == "production"
)


approval_success = (
    approval_result["success"] is True
    and approval_result["status"] == "approved"
)


pending_success = (
    len(pending_after_approval) == 0
)


destructive_success = (
    destructive_task["required"] is True
    and destructive_task["status"] == "pending"
    and destructive_task["category"] == "destructive"
)


rejection_success = (
    rejection_result["success"] is True
    and rejection_result["status"] == "rejected"
)


if (
    normal_success
    and production_success
    and approval_success
    and pending_success
    and destructive_success
    and rejection_success
):
    print(
        "INTERVENTION MANAGER TEST PASSED"
    )
else:
    print(
        "INTERVENTION MANAGER TEST FAILED"
    )