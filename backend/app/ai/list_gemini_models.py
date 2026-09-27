import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI API KEY: NOT FOUND")
    raise SystemExit(1)

print("GEMINI API KEY: FOUND")

try:
    client = genai.Client(
        api_key=api_key
    )

    models = client.models.list()

    print("\nAVAILABLE GENERATION MODELS:\n")

    for model in models:

        name = getattr(
            model,
            "name",
            ""
        )

        supported_methods = getattr(
            model,
            "supported_actions",
            None
        )

        if (
            "generateContent" in str(
                supported_methods
            )
            or "generate_content" in str(
                supported_methods
            )
        ):
            print(
                name,
                "|",
                supported_methods
            )

except Exception as error:

    print(
        "\nMODEL LIST FAILED:"
    )

    print(
        error
    )