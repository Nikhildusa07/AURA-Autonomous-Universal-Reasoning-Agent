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

    response = client.models.generate_content(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        ),
        contents="Reply with exactly: AURA API TEST OK"
    )

    print(
        "GEMINI API TEST: SUCCESS"
    )

    print(
        "MODEL RESPONSE:",
        response.text
    )

except Exception as error:

    print(
        "GEMINI API TEST: FAILED"
    )

    print(
        "ERROR:",
        error
    )