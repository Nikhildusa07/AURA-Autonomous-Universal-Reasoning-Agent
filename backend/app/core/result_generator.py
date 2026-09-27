import ast

from backend.app.models.task import Task


class ResultGenerator:

    def generate(self, goal: str, tasks: list[Task]):

        completed_tasks = []
        failed_tasks = []

        for task in tasks:

            if task.status == "completed":

                completed_tasks.append(
                    {
                        "task_id": task.id,
                        "description": task.description,
                        "result": task.result,
                    }
                )

            elif task.status == "failed":

                failed_tasks.append(
                    {
                        "task_id": task.id,
                        "description": task.description,
                        "error": task.error,
                    }
                )

            for subtask in getattr(
                task,
                "subtasks",
                []
            ):

                if subtask.status == "completed":

                    completed_tasks.append(
                        {
                            "task_id": subtask.id,
                            "description": subtask.description,
                            "result": subtask.result,
                        }
                    )

                elif subtask.status == "failed":

                    failed_tasks.append(
                        {
                            "task_id": subtask.id,
                            "description": subtask.description,
                            "error": subtask.error,
                        }
                    )

        status = (
            "completed"
            if not failed_tasks
            else "partial"
        )

        extracted_results = []

        for item in completed_tasks:

            extracted = self._extract_execution_result(
                item["result"]
            )

            if extracted:

                extracted_results.append(
                    {
                        "task_id":
                            item["task_id"],

                        "description":
                            item["description"],

                        "result":
                            extracted,
                    }
                )

        answer = self._generate_answer(
            goal,
            extracted_results
        )

        key_results = self._build_key_results(
            extracted_results
        )

        # -------------------------------------------------
        # IMPORTANT:
        # Never allow a raw Python dictionary to become
        # the user-facing answer.
        # -------------------------------------------------

        if not answer:

            answer = (
                f"AURA completed the objective: {goal}"
            )

        return {
            "goal":
                goal,

            "status":
                status,

            "summary":
                answer,

            "answer":
                answer,

            "key_results":
                key_results,

            "completed_tasks":
                completed_tasks,

            "failed_tasks":
                failed_tasks,

            "extracted_results":
                extracted_results,
        }

    # =====================================================
    # PARSE VALUE
    # =====================================================

    def _parse_value(self, value):

        if isinstance(
            value,
            (dict, list, tuple)
        ):

            return value

        if not isinstance(
            value,
            str
        ):

            return value

        text = value.strip()

        if not text:

            return value

        try:

            return ast.literal_eval(
                text
            )

        except Exception:

            return value

    # =====================================================
    # EXTRACT ACTUAL TOOL RESULT
    # =====================================================

    def _extract_execution_result(
        self,
        value,
        depth=0
    ):

        if depth > 10:

            return None

        value = self._parse_value(
            value
        )

        # -------------------------------------------------
        # Dictionary
        # -------------------------------------------------

        if isinstance(
            value,
            dict
        ):

            tool = value.get(
                "tool"
            )

            expression = value.get(
                "expression"
            )

            result = value.get(
                "result"
            )

            # ---------------------------------------------
            # Calculator
            # ---------------------------------------------

            if (
                tool == "calculator"
                and expression is not None
                and result is not None
            ):

                result = self._parse_value(
                    result
                )

                # Nested calculator response
                if isinstance(
                    result,
                    dict
                ):

                    inner_expression = (
                        result.get(
                            "expression"
                        )
                    )

                    inner_result = (
                        result.get(
                            "result"
                        )
                    )

                    if inner_result is not None:

                        return {
                            "type":
                                "calculation",

                            "expression":
                                inner_expression
                                or expression,

                            "result":
                                inner_result,
                        }

                return {
                    "type":
                        "calculation",

                    "expression":
                        expression,

                    "result":
                        result,
                }

            # ---------------------------------------------
            # Calculator response without tool field
            # ---------------------------------------------

            if (
                expression is not None
                and result is not None
            ):

                result = self._parse_value(
                    result
                )

                if isinstance(
                    result,
                    dict
                ):

                    inner_expression = (
                        result.get(
                            "expression"
                        )
                    )

                    inner_result = (
                        result.get(
                            "result"
                        )
                    )

                    if inner_result is not None:

                        return {
                            "type":
                                "calculation",

                            "expression":
                                inner_expression
                                or expression,

                            "result":
                                inner_result,
                        }

                return {
                    "type":
                        "calculation",

                    "expression":
                        expression,

                    "result":
                        result,
                }

            # ---------------------------------------------
            # Web research
            # ---------------------------------------------

            if (
                tool == "web_research"
            ):

                return {
                    "type":
                        "research",

                    "query":
                        value.get(
                            "query"
                        ),

                    "count":
                        value.get(
                            "count",
                            0
                        ),

                    "results":
                        value.get(
                            "results",
                            []
                        ),
                }

            # ---------------------------------------------
            # Browser / computer
            # ---------------------------------------------

            if tool in (
                "browser",
                "computer"
            ):

                return {
                    "type":
                        tool,

                    "url":
                        value.get(
                            "url"
                        ),

                    "title":
                        value.get(
                            "title"
                        ),

                    "text":
                        value.get(
                            "text"
                        ),
                }

            # ---------------------------------------------
            # Search nested dictionary values
            # ---------------------------------------------

            for nested_value in value.values():

                extracted = (
                    self._extract_execution_result(
                        nested_value,
                        depth + 1
                    )
                )

                if extracted:

                    return extracted

        # -------------------------------------------------
        # List
        # -------------------------------------------------

        elif isinstance(
            value,
            (list, tuple)
        ):

            for item in value:

                extracted = (
                    self._extract_execution_result(
                        item,
                        depth + 1
                    )
                )

                if extracted:

                    return extracted

        return None

    # =====================================================
    # GENERATE USER-FACING ANSWER
    # =====================================================

    def _generate_answer(
        self,
        goal,
        extracted_results
    ):

        if not extracted_results:

            return (
                f"AURA completed the objective: {goal}"
            )

        # -------------------------------------------------
        # Use the most recent meaningful result
        # -------------------------------------------------

        latest = extracted_results[-1].get(
            "result"
        )

        if not isinstance(
            latest,
            dict
        ):

            return str(latest)

        result_type = latest.get(
            "type"
        )

        # =================================================
        # CALCULATION
        # =================================================

        if result_type == "calculation":

            expression = latest.get(
                "expression"
            )

            result = latest.get(
                "result"
            )

            # Never stringify the entire calculator
            # dictionary.
            if isinstance(
                result,
                dict
            ):

                result = result.get(
                    "result",
                    result
                )

            if expression is not None:

                return (
                    f"{expression} = {result}"
                )

            return str(result)

        # =================================================
        # RESEARCH
        # =================================================

        if result_type == "research":

            query = latest.get(
                "query"
            )

            results = latest.get(
                "results",
                []
            )

            lines = []

            if query:

                lines.append(
                    f"Research completed for: {query}"
                )

            for index, item in enumerate(
                results[:5],
                start=1
            ):

                if not isinstance(
                    item,
                    dict
                ):

                    continue

                title = item.get(
                    "title",
                    "Untitled result"
                )

                snippet = item.get(
                    "snippet",
                    ""
                )

                lines.append(
                    f"{index}. {title}"
                )

                if snippet:

                    lines.append(
                        f"   {snippet}"
                    )

            return "\n".join(
                lines
            )

        # =================================================
        # BROWSER / COMPUTER
        # =================================================

        if result_type in (
            "browser",
            "computer"
        ):

            return str(
                latest.get(
                    "text"
                )
                or
                latest.get(
                    "title"
                )
                or
                latest.get(
                    "url"
                )
                or
                "Browser interaction completed."
            )

        # =================================================
        # GENERIC
        # =================================================

        result = latest.get(
            "result"
        )

        if result is not None:

            if isinstance(
                result,
                dict
            ):

                inner_result = result.get(
                    "result"
                )

                if inner_result is not None:

                    return str(
                        inner_result
                    )

            return str(result)

        return (
            f"AURA completed the objective: {goal}"
        )

    # =====================================================
    # KEY RESULTS
    # =====================================================

    def _build_key_results(
        self,
        extracted_results
    ):

        key_results = []

        for item in extracted_results:

            result = item.get(
                "result"
            )

            if not isinstance(
                result,
                dict
            ):

                continue

            result_type = result.get(
                "type"
            )

            # ---------------------------------------------
            # Calculation
            # ---------------------------------------------

            if result_type == "calculation":

                calculation_result = result.get(
                    "result"
                )

                if isinstance(
                    calculation_result,
                    dict
                ):

                    calculation_result = (
                        calculation_result.get(
                            "result",
                            calculation_result
                        )
                    )

                key_results.append(
                    {
                        "type":
                            "calculation",

                        "expression":
                            result.get(
                                "expression"
                            ),

                        "result":
                            calculation_result,
                    }
                )

            # ---------------------------------------------
            # Research
            # ---------------------------------------------

            elif result_type == "research":

                results = result.get(
                    "results",
                    []
                )

                key_results.append(
                    {
                        "type":
                            "research",

                        "query":
                            result.get(
                                "query"
                            ),

                        "result_count":
                            len(results),
                    }
                )

            # ---------------------------------------------
            # Browser
            # ---------------------------------------------

            elif result_type in (
                "browser",
                "computer"
            ):

                key_results.append(
                    {
                        "type":
                            result_type,

                        "title":
                            result.get(
                                "title"
                            ),

                        "url":
                            result.get(
                                "url"
                            ),
                    }
                )

        return key_results


result_generator = ResultGenerator()