import re

from backend.app.tools.registry import tool_registry


class SmartToolSelector:

    def __init__(self):
        self.registry = tool_registry

    def select_tool(self, task_description: str):

        description = task_description.strip()

        if not description:
            return {
                "tool": "none",
                "arguments": {},
                "reason": "Task description is empty.",
                "selection_method": "local_rule"
            }

        # ---------------------------------------------------------
        # 1. CALCULATOR
        # ---------------------------------------------------------

        expression = self._extract_expression(
            description
        )

        if expression:

            return {
                "tool": "calculator",
                "arguments": {
                    "expression": expression
                },
                "reason": (
                    "Local rule selected calculator "
                    "for a mathematical expression."
                ),
                "selection_method": "local_rule"
            }

        # ---------------------------------------------------------
        # 2. BROWSER
        # ---------------------------------------------------------

        url = self._extract_url(
            description
        )

        browser_keywords = (
            "open",
            "browse",
            "visit",
            "webpage",
            "website"
        )

        if (
            url
            and any(
                keyword in description.lower()
                for keyword in browser_keywords
            )
        ):

            return {
                "tool": "browser",
                "arguments": {
                    "url": url
                },
                "reason": (
                    "Local rule selected browser "
                    "for an explicit URL."
                ),
                "selection_method": "local_rule"
            }

        # ---------------------------------------------------------
        # 3. WEB RESEARCH
        # ---------------------------------------------------------

        research_keywords = (
            "search",
            "research",
            "find current",
            "latest",
            "look up",
            "news",
            "information about"
        )

        if any(
            keyword in description.lower()
            for keyword in research_keywords
        ):

            return {
                "tool": "web_research",
                "arguments": {
                    "query": description
                },
                "reason": (
                    "Local rule selected web research "
                    "for a research-oriented task."
                ),
                "selection_method": "local_rule"
            }

        # ---------------------------------------------------------
        # 4. REASONING / PRESENTATION TASKS
        # ---------------------------------------------------------

        reasoning_keywords = (
            "identify",
            "determine",
            "understand",
            "explain",
            "verify",
            "validate",
            "analyze",
            "interpret",
            "format",
            "present",
            "summarize",
            "describe"
        )

        if any(
            keyword in description.lower()
            for keyword in reasoning_keywords
        ):

            return {
                "tool": "none",
                "arguments": {},
                "reason": (
                    "No registered execution tool is required "
                    "for this reasoning or presentation task."
                ),
                "selection_method": "local_rule"
            }

        # ---------------------------------------------------------
        # 5. EXISTING LLM TOOL SELECTOR
        # ---------------------------------------------------------

        try:

            from backend.app.ai import tool_selector

            selector = getattr(
                tool_selector,
                "llm_tool_selector",
                None
            )

            if selector is None:

                selector = getattr(
                    tool_selector,
                    "tool_selector",
                    None
                )

            if selector is None:

                selector_class = getattr(
                    tool_selector,
                    "LLMToolSelector",
                    None
                )

                if selector_class is not None:
                    selector = selector_class()

            if selector is None:

                return {
                    "tool": "none",
                    "arguments": {},
                    "reason": (
                        "No LLM tool selector is available."
                    ),
                    "selection_method": "local_fallback"
                }

            result = selector.select_tool(
                description
            )

            return {
                **result,
                "selection_method": "llm"
            }

        except Exception as error:

            return {
                "tool": "none",
                "arguments": {},
                "reason": (
                    f"LLM tool selection failed: {error}"
                ),
                "selection_method": "llm_fallback"
            }

    def _extract_expression(
        self,
        description: str
    ):

        text = description.lower().strip()

        # Direct expressions such as:
        # 2500 * 4
        # 20 + 30
        # 100 / 5
        direct_expression = re.search(
            r"(?<!\w)"
            r"\d+(?:\.\d+)?"
            r"\s*[+\-*/]"
            r"\s*\d+(?:\.\d+)?"
            r"(?:"
            r"\s*[+\-*/]"
            r"\s*\d+(?:\.\d+)?"
            r")*"
            r"(?!\w)",
            text
        )

        if direct_expression:

            return direct_expression.group(
                0
            ).strip()

        # multiplied by
        multiplication = re.search(
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:multiplied by|times|x)"
            r"\s*"
            r"(\d+(?:\.\d+)?)",
            text
        )

        if multiplication:

            return (
                f"{multiplication.group(1)} "
                f"* "
                f"{multiplication.group(2)}"
            )

        # plus
        addition = re.search(
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:plus|added to)"
            r"\s*"
            r"(\d+(?:\.\d+)?)",
            text
        )

        if addition:

            return (
                f"{addition.group(1)} "
                f"+ "
                f"{addition.group(2)}"
            )

        # minus
        subtraction = re.search(
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:minus|subtracted from)"
            r"\s*"
            r"(\d+(?:\.\d+)?)",
            text
        )

        if subtraction:

            return (
                f"{subtraction.group(1)} "
                f"- "
                f"{subtraction.group(2)}"
            )

        # divided by
        division = re.search(
            r"(\d+(?:\.\d+)?)"
            r"\s*(?:divided by|over)"
            r"\s*"
            r"(\d+(?:\.\d+)?)",
            text
        )

        if division:

            return (
                f"{division.group(1)} "
                f"/ "
                f"{division.group(2)}"
            )

        return None

    def _extract_url(
        self,
        description: str
    ):

        match = re.search(
            r"https?://[^\s]+",
            description
        )

        if not match:
            return None

        return match.group(0).rstrip(
            ".,!?;:)"
        )


smart_tool_selector = SmartToolSelector()