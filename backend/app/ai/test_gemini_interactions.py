import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


if not api_key:
    print("GEMINI API KEY: NOT FOUND")
    raise SystemExit(1)


print("GEMINI API KEY: FOUND")
print("GEMINI MODEL:", model)


try:
    client = genai.Client(
        api_key=api_key
    )

    interaction = client.interactions.create(
        model=model,
        input="Reply with exactly: AURA INTERACTIONS API TEST OK",
        timeout=60
    )

    print("\nGEMINI INTERACTIONS API TEST: SUCCESS")

    print(
        "MODEL RESPONSE:",
        interaction.output_text
    )

except Exception as error:

    print("\nGEMINI INTERACTIONS API TEST: FAILED")

    print("ERROR:")
    print(error)