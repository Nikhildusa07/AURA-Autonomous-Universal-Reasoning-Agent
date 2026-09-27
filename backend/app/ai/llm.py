import os

# Prevent the Google SDK from automatically selecting GOOGLE_API_KEY.
os.environ.pop("GOOGLE_API_KEY", None)

from dotenv import load_dotenv

load_dotenv()

from google import genai


class LLMService:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        self.timeout = 60

    def generate(self, prompt: str) -> str:
        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=prompt,
                timeout=self.timeout
            )

            if not interaction.output_text:
                raise RuntimeError(
                    "LLM returned an empty response."
                )

            return interaction.output_text.strip()

        except Exception as error:
            raise RuntimeError(
                f"LLM request failed: {error}"
            ) from error


llm_service = LLMService()