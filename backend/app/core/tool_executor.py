from backend.app.tools.registry import tool_registry


class ToolExecutor:
    def execute(self, tool_name: str, **kwargs):
        tool = tool_registry.get_tool(tool_name)

        if tool is None:
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Tool '{tool_name}' not found."
            }

        try:
            result = tool.execute(**kwargs)

            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }

        except Exception as error:
            return {
                "success": False,
                "tool": tool_name,
                "error": str(error)
            }