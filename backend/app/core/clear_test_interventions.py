from backend.app.memory.intervention_memory import (
    intervention_memory
)


test_task_ids = [
    501,
    502,
    503,
    504
]


deleted = 0


for task_id in test_task_ids:

    if intervention_memory.delete_request(
        task_id
    ):
        deleted += 1


print(
    f"Deleted {deleted} test intervention request(s)."
)


remaining = (
    intervention_memory.get_pending_requests()
)


print(
    "Remaining pending requests:",
    remaining
)