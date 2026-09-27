from backend.app.core.context_aware_executor import (
    context_aware_executor
)


def main():
    print("=" * 70)
    print("AURA CONTEXT-AWARE EXECUTOR TEST")
    print("=" * 70)

    context_aware_executor.clear_context()

    print("\nTASK 1: Research")
    result_1 = context_aware_executor.execute(
        task_id=1,
        task_description="Research the latest Python version"
    )

    print(result_1)

    print("\n" + "=" * 70)
    print("TASK 2: Use Previous Research")
    result_2 = context_aware_executor.execute(
        task_id=2,
        task_description=(
            "Verify the Python version found by the previous "
            "research task."
        )
    )

    print(result_2)

    print("\n" + "=" * 70)
    print("FINAL CONTEXT")
    print("=" * 70)

    print(
        context_aware_executor.get_context()
    )

    print("\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()