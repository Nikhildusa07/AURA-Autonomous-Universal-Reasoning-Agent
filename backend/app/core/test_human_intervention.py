from backend.app.core.human_intervention import human_intervention


print("\n========== HUMAN INTERVENTION TEST ==========")


# 1. Create an intervention request
approval_request = human_intervention.request_approval(
    task_id=101,
    task_description="Deploy AURA to production",
    reason="Production deployment requires human approval."
)

print("\nApproval Request:")
print(approval_request)


# 2. Check pending requests
pending_requests = (
    human_intervention.get_pending_requests()
)

print("\nPending Requests:")
print(pending_requests)


# 3. Approve the request
approval_response = human_intervention.respond(
    task_id=101,
    response="Approved for deployment."
)

print("\nApproval Response:")
print(approval_response)


# 4. Check pending requests again
pending_after_approval = (
    human_intervention.get_pending_requests()
)

print("\nPending After Approval:")
print(pending_after_approval)


# 5. Create another request and reject it
rejection_request = human_intervention.request_approval(
    task_id=102,
    task_description="Delete production database",
    reason="Destructive operation requires human approval."
)

print("\nRejection Request:")
print(rejection_request)


rejection_response = human_intervention.reject(
    task_id=102,
    response="Rejected. Do not delete the database."
)

print("\nRejection Response:")
print(rejection_response)


# 6. Get all intervention requests
all_requests = (
    human_intervention.get_all_requests()
)

print("\nAll Requests:")
print(all_requests)


print("\n========== TEST RESULT ==========")


approval_success = (
    approval_request["required"]
    and approval_request["status"] == "pending"
    and approval_response["success"]
    and approval_response["status"] == "approved"
)


rejection_success = (
    rejection_request["required"]
    and rejection_request["status"] == "pending"
    and rejection_response["success"]
    and rejection_response["status"] == "rejected"
)


pending_success = (
    len(pending_after_approval) == 0
)


if (
    approval_success
    and rejection_success
    and pending_success
    and len(all_requests) == 2
):
    print(
        "HUMAN INTERVENTION TEST PASSED"
    )
else:
    print(
        "HUMAN INTERVENTION TEST FAILED"
    )