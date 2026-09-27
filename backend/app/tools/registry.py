from backend.app.tools.tool import Tool
from backend.app.tools.calculator import CalculatorTool
from backend.app.tools.web_research import WebResearchTool
from backend.app.tools.browser import BrowserTool


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str):
        return self._tools.get(name)

    def list_tools(self):
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self._tools.values()
        ]


tool_registry = ToolRegistry()

tool_registry.register(CalculatorTool())
tool_registry.register(WebResearchTool())
tool_registry.register(BrowserTool())