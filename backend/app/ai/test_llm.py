from backend.app.ai.llm import llm_service


response = llm_service.generate(
    "Respond with exactly: AURA LLM connection successful"
)

print(response)