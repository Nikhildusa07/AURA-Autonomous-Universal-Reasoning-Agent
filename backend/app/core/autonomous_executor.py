from backend.app.ai.smart_tool_selector import smart_tool_selector
from backend.app.core.reasoning_executor import reasoning_executor
from backend.app.core.tool_executor import ToolExecutor
from backend.app.core.tool_validator import tool_validator


class AutonomousExecutor:

    def __init__(self):
        self.tool_executor = ToolExecutor()
        self.reasoning_executor = reasoning_executor

    def execute(
        self,
        task_description: str,
        context: dict | None = None
    ):
        try:
            selection = smart_tool_selector.select_tool(
                task_description
            )

            selected_tool = selection["tool"]

            tool_arguments = selection.get(
                "arguments",
                {}
            )

            selection_method = selection.get(
                "selection_method",
                "unknown"
            )

            selection_reason = selection.get(
                "reason",
                ""
            )

            # --------------------------------------------------
            # REASONING PATH
            # --------------------------------------------------

            if selected_tool == "none":

                reasoning_result = (
                    self.reasoning_executor.execute(
                        task_description=task_description,
                        context=context
                    )
                )

                return {
                    "success": reasoning_result["success"],
                    "task": task_description,
                    "tool": "none",
                    "execution_type": "reasoning",
                    "selection_reason": selection_reason,
                    "selection_method": selection_method,
                    "arguments": tool_arguments,
                    "execution": reasoning_result
                }

            # --------------------------------------------------
            # TOOL VALIDATION
            # --------------------------------------------------

            validation = tool_validator.validate(
                selected_tool,
                tool_arguments
            )

            if not validation["valid"]:
                return {
                    "success": False,
                    "task": task_description,
                    "tool": selected_tool,
                    "execution_type": "tool",
                    "reason": selection_reason,
                    "arguments": tool_arguments,
                    "selection_method": selection_method,
                    "validation": validation,
                    "error": validation["error"]
                }

            validated_arguments = validation["arguments"]

            # --------------------------------------------------
            # TOOL EXECUTION
            # --------------------------------------------------

            execution_result = self.tool_executor.execute(
                selected_tool,
                **validated_arguments
            )

            return {
                "success": execution_result["success"],
                "task": task_description,
                "tool": selected_tool,
                "execution_type": "tool",
                "selection_reason": selection_reason,
                "selection_method": selection_method,
                "arguments": validated_arguments,
                "validation": validation,
                "execution": execution_result
            }

        except Exception as error:

            return {
                "success": False,
                "task": task_description,
                "tool": None,
                "execution_type": "error",
                "selection_method": "error",
                "error": str(error)
            }


autonomous_executor = AutonomousExecutor()