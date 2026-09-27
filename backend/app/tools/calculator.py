from backend.app.tools.tool import Tool


class CalculatorTool(Tool):
    name = "calculator"
    description = "Performs basic mathematical calculations."

    def execute(self, expression: str):
        try:
            allowed_characters = "0123456789+-*/(). "

            if not all(character in allowed_characters for character in expression):
                return {
                    "success": False,
                    "error": "Invalid characters in expression."
                }

            result = eval(expression, {"__builtins__": {}}, {})

            return {
                "success": True,
                "expression": expression,
                "result": result
            }

        except Exception as error:
            return {
                "success": False,
                "expression": expression,
                "error": str(error)
            }