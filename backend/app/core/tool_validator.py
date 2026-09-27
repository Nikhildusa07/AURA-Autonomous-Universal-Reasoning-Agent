from urllib.parse import urlparse

from backend.app.tools.registry import tool_registry


class ToolValidator:

    def validate(
        self,
        tool_name: str,
        arguments: dict
    ) -> dict:

        if not tool_name:
            return {
                "valid": False,
                "error": "Tool name is required."
            }

        if tool_name == "none":
            return {
                "valid": False,
                "error": "No tool was selected."
            }

        tool = tool_registry.get_tool(
            tool_name
        )

        if tool is None:
            return {
                "valid": False,
                "error": (
                    f"Tool '{tool_name}' is not registered."
                )
            }

        if not isinstance(arguments, dict):
            return {
                "valid": False,
                "error": "Tool arguments must be a dictionary."
            }

        if tool_name == "calculator":
            return self._validate_calculator(
                arguments
            )

        if tool_name == "web_research":
            return self._validate_web_research(
                arguments
            )

        if tool_name == "browser":
            return self._validate_browser(
                arguments
            )

        return {
            "valid": True,
            "tool": tool_name,
            "arguments": arguments
        }

    def _validate_calculator(
        self,
        arguments: dict
    ) -> dict:

        expression = arguments.get(
            "expression"
        )

        if not expression:
            return {
                "valid": False,
                "error": (
                    "Calculator requires "
                    "'expression'."
                )
            }

        if not isinstance(
            expression,
            str
        ):
            return {
                "valid": False,
                "error": (
                    "Calculator expression "
                    "must be a string."
                )
            }

        return {
            "valid": True,
            "tool": "calculator",
            "arguments": {
                "expression": expression.strip()
            }
        }

    def _validate_web_research(
        self,
        arguments: dict
    ) -> dict:

        query = arguments.get(
            "query"
        )

        if not query:
            return {
                "valid": False,
                "error": (
                    "Web research requires "
                    "'query'."
                )
            }

        if not isinstance(
            query,
            str
        ):
            return {
                "valid": False,
                "error": (
                    "Search query must be a string."
                )
            }

        max_results = arguments.get(
            "max_results",
            5
        )

        try:
            max_results = int(
                max_results
            )
        except (
            TypeError,
            ValueError
        ):
            return {
                "valid": False,
                "error": (
                    "'max_results' must be "
                    "an integer."
                )
            }

        max_results = max(
            1,
            min(max_results, 10)
        )

        return {
            "valid": True,
            "tool": "web_research",
            "arguments": {
                "query": query.strip(),
                "max_results": max_results
            }
        }

    def _validate_browser(
        self,
        arguments: dict
    ) -> dict:

        url = arguments.get(
            "url"
        )

        if not url:
            return {
                "valid": False,
                "error": (
                    "Browser requires 'url'."
                )
            }

        if not isinstance(
            url,
            str
        ):
            return {
                "valid": False,
                "error": (
                    "Browser URL must be a string."
                )
            }

        url = url.strip()

        parsed_url = urlparse(
            url
        )

        if parsed_url.scheme not in (
            "http",
            "https"
        ):
            return {
                "valid": False,
                "error": (
                    "Browser URL must use "
                    "http:// or https://."
                )
            }

        if not parsed_url.netloc:
            return {
                "valid": False,
                "error": (
                    "Browser URL is invalid."
                )
            }

        max_text_length = arguments.get(
            "max_text_length",
            5000
        )

        try:
            max_text_length = int(
                max_text_length
            )
        except (
            TypeError,
            ValueError
        ):
            max_text_length = 5000

        max_text_length = max(
            500,
            min(max_text_length, 20000)
        )

        link_text = arguments.get(
            "link_text"
        )

        if link_text is not None:
            if not isinstance(
                link_text,
                str
            ):
                return {
                    "valid": False,
                    "error": (
                        "'link_text' must "
                        "be a string."
                    )
                }

            link_text = link_text.strip()

            if not link_text:
                link_text = None

        link_index = arguments.get(
            "link_index"
        )

        if link_index is not None:

            try:
                link_index = int(
                    link_index
                )
            except (
                TypeError,
                ValueError
            ):
                return {
                    "valid": False,
                    "error": (
                        "'link_index' must "
                        "be an integer."
                    )
                }

            if link_index < 0:
                return {
                    "valid": False,
                    "error": (
                        "'link_index' cannot "
                        "be negative."
                    )
                }

        if (
            link_text is not None
            and link_index is not None
        ):
            return {
                "valid": False,
                "error": (
                    "Use either 'link_text' "
                    "or 'link_index', not both."
                )
            }

        validated_arguments = {
            "url": url,
            "max_text_length": max_text_length
        }

        if link_text is not None:
            validated_arguments[
                "link_text"
            ] = link_text

        if link_index is not None:
            validated_arguments[
                "link_index"
            ] = link_index

        return {
            "valid": True,
            "tool": "browser",
            "arguments": validated_arguments
        }


tool_validator = ToolValidator()