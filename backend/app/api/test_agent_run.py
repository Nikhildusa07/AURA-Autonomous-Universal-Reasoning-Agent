from backend.app.api.agent import AgentRequest
from backend.app.api.agent import run_agent


def main():
    request = AgentRequest(
        goal="Calculate 2500 multiplied by 4"
    )

    print("=" * 60)
    print("AURA AGENT RUN TEST")
    print("=" * 60)

    print("\nGOAL:")
    print(request.goal)

    try:
        result = run_agent(request)

        print("\n" + "=" * 60)
        print("AGENT EXECUTION RESULT")
        print("=" * 60)

        print(result)

        print("\n" + "=" * 60)
        print("TEST COMPLETED")
        print("=" * 60)

    except Exception as error:
        print("\n" + "=" * 60)
        print("AGENT EXECUTION FAILED")
        print("=" * 60)

        print("ERROR:")
        print(error)

        raise


if __name__ == "__main__":
    main()