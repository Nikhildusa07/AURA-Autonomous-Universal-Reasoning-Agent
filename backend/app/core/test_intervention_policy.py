from backend.app.core.intervention_policy import (
    intervention_policy
)


print("\n========== INTERVENTION POLICY TEST ==========")


test_cases = [
    {
        "task": "Calculate 500 multiplied by 20",
        "expected": False
    },
    {
        "task": "Search for the official FastAPI documentation",
        "expected": False
    },
    {
        "task": "Deploy AURA to production",
        "expected": True
    },
    {
        "task": "Delete the production database",
        "expected": True
    },
    {
        "task": "Send an email to the administrator",
        "expected": True
    },
    {
        "task": "Use the API key to access the service",
        "expected": True
    }
]


passed = 0


for index, test_case in enumerate(
    test_cases,
    start=1
):

    task = test_case["task"]
    expected = test_case["expected"]

    result = intervention_policy.evaluate(
        task
    )

    actual = result[
        "requires_intervention"
    ]

    print(f"\nTest {index}:")
    print("Task:", task)
    print("Requires intervention:", actual)
    print("Category:", result["category"])
    print(
        "Matched categories:",
        result["matched_categories"]
    )

    if actual == expected:
        print("Result: PASS")
        passed += 1
    else:
        print("Result: FAIL")


print("\n========== TEST RESULT ==========")


if passed == len(test_cases):
    print(
        "INTERVENTION POLICY TEST PASSED"
    )
else:
    print(
        "INTERVENTION POLICY TEST FAILED"
    )

print(
    f"Passed: {passed}/{len(test_cases)}"
)