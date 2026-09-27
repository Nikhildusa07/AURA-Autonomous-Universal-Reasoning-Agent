from backend.app.tools.web_research import WebResearchTool


tool = WebResearchTool()

result = tool.execute(
    query="FastAPI official documentation",
    max_results=5
)

print("\nWeb Research Result:\n")
print(result)