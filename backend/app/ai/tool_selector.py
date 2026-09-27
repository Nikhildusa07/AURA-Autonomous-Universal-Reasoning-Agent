import json
import re

from backend.app.ai.llm import llm_service
from backend.app.tools.registry import tool_registry


class ToolSelector:

    def select_tool(self, task_description: str) -> dict:
        available_tools = tool_registry.list_tools()

        tools_text = json.dumps(
            available_tools,
            indent=2
        )

        prompt = f"""
You are the tool selection engine of AURA, an autonomous AI agent.

Your job is to select the most appropriate available tool and
generate the arguments required to execute that tool.

Task:
{task_description}

Available tools:
{tools_text}

Tool capabilities:

1. calculator
   - Performs mathematical calculations.
   - Required argument:
     "expression"

2. web_research
   - Searches the web for information.
   - Required argument:
     "query"
   - Optional argument:
     "max_results" between 1 and 10

3. browser
   - Opens a webpage.
   - Extracts webpage text and links.
   - Can follow a link by text or index.
   - Required argument:
     "url"
   - Optional arguments:
     "max_text_length"
     "link_text"
     "link_index"

Rules:
1. Select only a tool from the available tools.
2. Select the tool that best matches the task.
3. If no tool is appropriate, return "none".
4. Never invent a tool.
5. Generate valid arguments for the selected tool.
6. For calculator:
   - "expression" must contain the mathematical expression.
7. For web_research:
   - "query" must contain the actual search query.
   - "max_results" must be an integer between 1 and 10.
8. For browser:
   - "url" must be a valid HTTP or HTTPS URL.
   - Use "link_text" when the task asks to follow a named link.
   - Use "link_index" only when a specific link index is provided.
9. Return ONLY valid JSON.
10. Do not use markdown or code fences.

Required format:

{{
    "tool": "calculator",
    "reason": "The task requires mathematical calculation.",
    "arguments": {{
        "expression": "30000 / 5"
    }}
}}

Browser example:

{{
    "tool": "browser",
    "reason": "The task requires opening and inspecting a webpage.",
    "arguments": {{
        "url": "https://fastapi.tiangolo.com/",
        "max_text_length": 5000
    }}
}}

Browser link-following example:

{{
    "tool": "browser",
    "reason": "The task requires opening the documentation and following the Tutorial link.",
    "arguments": {{
        "url": "https://fastapi.tiangolo.com/",
        "link_text": "Tutorial",
        "max_text_length": 5000
    }}
}}

If no suitable tool exists:

{{
    "tool": "none",
    "reason": "No available tool can perform this task.",
    "arguments": {{}}
}}
"""

        response = llm_service.generate(prompt)

        return self._parse_response(response)

    def _parse_response(self, response: str) -> dict:
        cleaned_response = response.strip()

        cleaned_response = re.sub(
            r"^```json\s*",
            "",
            cleaned_response,
            flags=re.IGNORECASE
        )

        cleaned_response = re.sub(
            r"\s*```$",
            "",
            cleaned_response
        )

        try:
            selection = json.loads(
                cleaned_response
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                f"LLM tool selector returned invalid JSON: {error}"
            )

        if not isinstance(selection, dict):
            raise ValueError(
                "Tool selector response must be a JSON object."
            )

        tool_name = selection.get("tool")
        reason = selection.get("reason", "")
        arguments = selection.get(
            "arguments",
            {}
        )

        if not tool_name:
            raise ValueError(
                "Tool selector did not specify a tool."
            )

        if not isinstance(arguments, dict):
            raise ValueError(
                "Tool selector arguments must be a JSON object."
            )

        if tool_name != "none":

            if tool_registry.get_tool(
                tool_name
            ) is None:
                raise ValueError(
                    f"LLM selected unavailable tool: {tool_name}"
                )

        return {
            "tool": str(tool_name),
            "reason": str(reason),
            "arguments": arguments
        }


tool_selector = ToolSelector()