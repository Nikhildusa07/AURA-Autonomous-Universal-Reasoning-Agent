from backend.app.api.agent import AgentRequest
from backend.app.api.agent import run_agent


def main():
    request = AgentRequest(
        goal=(
            "Research the latest Python version, "
            "identify its release date, and summarize "
            "three important features."
        )
    )

    print("=" * 70)
    print("AURA RESEARCH AGENT TEST")
    print("=" * 70)

    print("\nGOAL:")
    print(request.goal)

    print("\nStarting autonomous execution...\n")

    try:
        result = run_agent(request)

        print("\n" + "=" * 70)
        print("RESEARCH AGENT RESULT")
        print("=" * 70)

        print(result)

        print("\n" + "=" * 70)
        print("TEST COMPLETED")
        print("=" * 70)

    except Exception as error:
        print("\n" + "=" * 70)
        print("RESEARCH AGENT FAILED")
        print("=" * 70)

        print("ERROR:")
        print(error)

        raise


if __name__ == "__main__":
    main()