from backend.app.ai.tool_selector import tool_selector


task = "Find the official FastAPI documentation."

print("\nTask:")
print(task)

selection = tool_selector.select_tool(task)

print("\nTool Selection:")
print(selection)