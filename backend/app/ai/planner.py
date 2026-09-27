from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any

from backend.app.ai.llm import LLMService


class LLMPlanner:
    """
    AURA planner with a Gemini circuit breaker.

    Behaviour:
    1. Try Gemini when it is available.
    2. If Gemini returns 429/rate-limit/quota error:
       - disable Gemini for the current day
       - persist that state locally
       - immediately use the local planner
    3. Subsequent requests on the same day do NOT call Gemini again.
    4. Local planning continues normally.
    """

    STATE_FILE = (
        Path(__file__).resolve().parents[2]
        / ".aura_llm_state.json"
    )

    def __init__(self):
        self.llm = None
        self.gemini_disabled = False
        self.disable_reason = None
        self.disabled_date = None

        self._load_circuit_breaker_state()

    # =====================================================
    # PUBLIC PLAN METHOD
    # =====================================================

    def create_plan(
        self,
        goal: str
    ) -> list[dict[str, Any]]:

        goal = (goal or "").strip()

        if not goal:
            raise ValueError(
                "Goal cannot be empty."
            )

        # -------------------------------------------------
        # If Gemini has already been disabled for today,
        # NEVER make another Gemini request.
        # -------------------------------------------------

        if self._gemini_is_disabled_today():

            print(
                "Gemini planner disabled for today. "
                "Using local fallback planner."
            )

            return self._local_plan(goal)

        # -------------------------------------------------
        # Try Gemini
        # -------------------------------------------------

        try:

            if self.llm is None:

                self.llm = LLMService()

            print(
                "Using Gemini planner..."
            )

            plan = self._create_llm_plan(
                goal
            )

            if plan:

                return plan

            print(
                "Gemini returned no usable plan. "
                "Using local fallback planner."
            )

            return self._local_plan(goal)

        except Exception as error:

            error_text = str(
                error
            ).lower()

            # =============================================
            # RATE LIMIT / QUOTA
            # =============================================

            if self._is_rate_limit_error(
                error_text
            ):

                self._disable_gemini(
                    reason="rate_limit"
                )

                print(
                    "Gemini rate limit reached. "
                    "Gemini planner disabled for today. "
                    "Using local fallback planner."
                )

                return self._local_plan(
                    goal
                )

            # =============================================
            # OTHER GEMINI FAILURE
            # =============================================

            print(
                "LLM planner unavailable. "
                "Using local fallback planner."
            )

            print(
                f"Planner error: {error}"
            )

            return self._local_plan(
                goal
            )

    # =====================================================
    # GEMINI PLAN
    # =====================================================

    def _create_llm_plan(
        self,
        goal: str
    ) -> list[dict[str, Any]]:

        prompt = f"""
You are the planning engine of AURA,
an autonomous AI agent.

Break the following objective into
clear executable subtasks.

OBJECTIVE:
{goal}

Return ONLY valid JSON.

Required format:

[
  {{
    "description": "subtask description",
    "priority": 1
  }}
]

Priority rules:

1 = high priority
2 = normal priority
3 = low priority

Rules:

- Create practical executable subtasks.
- Do not include explanations outside JSON.
- Do not include markdown.
- Do not include the final answer.
- Avoid duplicate subtasks.
- Keep the number of subtasks reasonable.
"""

        response = self.llm.generate(
            prompt
        )

        return self._parse_llm_response(
            response
        )

    # =====================================================
    # PARSE GEMINI RESPONSE
    # =====================================================

    def _parse_llm_response(
        self,
        response: str
    ) -> list[dict[str, Any]]:

        if not response:

            return []

        text = response.strip()

        # -------------------------------------------------
        # Remove markdown code fences
        # -------------------------------------------------

        text = re.sub(
            r"^```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"```$",
            "",
            text
        )

        text = text.strip()

        # -------------------------------------------------
        # Find JSON array if extra text exists
        # -------------------------------------------------

        start = text.find("[")
        end = text.rfind("]")

        if start != -1 and end != -1:

            text = text[
                start:end + 1
            ]

        try:

            data = json.loads(
                text
            )

        except Exception:

            return []

        if not isinstance(
            data,
            list
        ):

            return []

        normalized = []

        for item in data:

            if isinstance(
                item,
                str
            ):

                description = (
                    item.strip()
                )

                priority = 2

            elif isinstance(
                item,
                dict
            ):

                description = str(
                    item.get(
                        "description",
                        item.get(
                            "task",
                            item.get(
                                "name",
                                ""
                            )
                        )
                    )
                ).strip()

                priority = self._normalize_priority(
                    item.get(
                        "priority",
                        2
                    )
                )

            else:

                continue

            if not description:

                continue

            normalized.append(
                {
                    "description":
                        description,

                    "priority":
                        priority
                }
            )

        return normalized

    # =====================================================
    # LOCAL FALLBACK PLANNER
    # =====================================================

    def _local_plan(
        self,
        goal: str
    ) -> list[dict[str, Any]]:

        text = goal.strip()
        lower = text.lower()

        # =================================================
        # CALCULATION
        # =================================================

        if self._looks_like_calculation(
            lower
        ):

            return [
                {
                    "description":
                        f"Identify the numerical values "
                        f"and operation from: {goal}",

                    "priority": 1
                },
                {
                    "description":
                        f"Execute the required calculation: "
                        f"{goal}",

                    "priority": 1
                },
                {
                    "description":
                        "Verify the calculated result "
                        "for numerical accuracy.",

                    "priority": 2
                },
                {
                    "description":
                        "Format and present the final "
                        "calculated result.",

                    "priority": 2
                }
            ]

        # =================================================
        # RESEARCH
        # =================================================

        if self._looks_like_research(
            lower
        ):

            return [
                {
                    "description":
                        f"Research the requested information: "
                        f"{goal}",

                    "priority": 1
                },
                {
                    "description":
                        "Identify and verify the most "
                        "relevant findings.",

                    "priority": 1
                },
                {
                    "description":
                        "Analyze the researched information "
                        "and extract the important details.",

                    "priority": 2
                },
                {
                    "description":
                        "Format and present the final "
                        "research result.",

                    "priority": 2
                }
            ]

        # =================================================
        # WEB / WEBSITE
        # =================================================

        if self._looks_like_web_task(
            lower
        ):

            return [
                {
                    "description":
                        f"Open and inspect the relevant "
                        f"website or web resource for: {goal}",

                    "priority": 1
                },
                {
                    "description":
                        "Extract the information required "
                        "to complete the objective.",

                    "priority": 1
                },
                {
                    "description":
                        "Verify the extracted information.",

                    "priority": 2
                },
                {
                    "description":
                        "Present the final result.",

                    "priority": 2
                }
            ]

        # =================================================
        # CREATE / BUILD / DEVELOP
        # =================================================

        if any(
            keyword in lower
            for keyword in (
                "build",
                "create",
                "develop",
                "make",
                "implement"
            )
        ):

            return [
                {
                    "description":
                        f"Understand the requirements "
                        f"for: {goal}",

                    "priority": 1
                },
                {
                    "description":
                        f"Execute the required work "
                        f"for: {goal}",

                    "priority": 1
                },
                {
                    "description":
                        "Review the completed work "
                        "for correctness.",

                    "priority": 2
                },
                {
                    "description":
                        "Verify and present the final result.",

                    "priority": 2
                }
            ]

        # =================================================
        # COMPARE
        # =================================================

        if any(
            keyword in lower
            for keyword in (
                "compare",
                "comparison",
                "difference",
                "versus",
                " vs "
            )
        ):

            return [
                {
                    "description":
                        f"Collect the relevant information "
                        f"for: {goal}",

                    "priority": 1
                },
                {
                    "description":
                        "Compare the identified information "
                        "using the requested criteria.",

                    "priority": 1
                },
                {
                    "description":
                        "Verify the comparison results.",

                    "priority": 2
                },
                {
                    "description":
                        "Present the comparison clearly.",

                    "priority": 2
                }
            ]

        # =================================================
        # GENERIC OBJECTIVE
        # =================================================

        return [
            {
                "description":
                    f"Understand the objective: {goal}",

                "priority": 1
            },
            {
                "description":
                    f"Execute the required actions "
                    f"to accomplish: {goal}",

                "priority": 1
            },
            {
                "description":
                    "Evaluate the completed work "
                    "against the objective.",

                "priority": 2
            },
            {
                "description":
                    "Verify the result and identify "
                    "any remaining issues.",

                "priority": 2
            },
            {
                "description":
                    "Format and present the final result.",

                "priority": 2
            }
        ]

    # =====================================================
    # CALCULATION DETECTION
    # =====================================================

    def _looks_like_calculation(
        self,
        text: str
    ) -> bool:

        calculation_words = (
            "calculate",
            "calculation",
            "multiply",
            "multiplied",
            "divide",
            "divided",
            "addition",
            "add",
            "subtract",
            "subtraction",
            "minus",
            "plus",
            "sum",
            "product",
            "percentage",
            "percent",
            "average",
            "factorial",
            "power",
            "square",
            "cube"
        )

        if any(
            word in text
            for word in calculation_words
        ):

            return True

        # Basic mathematical expression
        if re.search(
            r"\d+\s*[\+\-\*\/%]\s*\d+",
            text
        ):

            return True

        return False

    # =====================================================
    # RESEARCH DETECTION
    # =====================================================

    def _looks_like_research(
        self,
        text: str
    ) -> bool:

        research_words = (
            "research",
            "latest",
            "find information",
            "look up",
            "investigate",
            "search for",
            "find out",
            "study",
            "analyze information"
        )

        return any(
            word in text
            for word in research_words
        )

    # =====================================================
    # WEB DETECTION
    # =====================================================

    def _looks_like_web_task(
        self,
        text: str
    ) -> bool:

        web_words = (
            "website",
            "web page",
            "webpage",
            "open url",
            "open website",
            "browse",
            "browser",
            "visit"
        )

        return any(
            word in text
            for word in web_words
        )

    # =====================================================
    # PRIORITY
    # =====================================================

    def _normalize_priority(
        self,
        priority: Any
    ) -> int:

        try:

            value = int(
                priority
            )

        except (
            TypeError,
            ValueError
        ):

            value = 2

        return max(
            1,
            min(
                value,
                3
            )
        )

    # =====================================================
    # RATE LIMIT DETECTION
    # =====================================================

    def _is_rate_limit_error(
        self,
        error_text: str
    ) -> bool:

        rate_limit_terms = (
            "429",
            "rate limit",
            "rate_limit",
            "too many requests",
            "quota exceeded",
            "quota",
            "limit exceeded",
            "resource exhausted"
        )

        return any(
            term in error_text
            for term in rate_limit_terms
        )

    # =====================================================
    # CIRCUIT BREAKER STATE
    # =====================================================

    def _load_circuit_breaker_state(
        self
    ):

        try:

            if not self.STATE_FILE.exists():

                return

            with self.STATE_FILE.open(
                "r",
                encoding="utf-8"
            ) as file:

                state = json.load(
                    file
                )

            disabled_date = state.get(
                "disabled_date"
            )

            if (
                state.get(
                    "gemini_disabled"
                )
                and disabled_date ==
                date.today().isoformat()
            ):

                self.gemini_disabled = True

                self.disable_reason = (
                    state.get(
                        "reason"
                    )
                )

                self.disabled_date = (
                    disabled_date
                )

        except Exception:

            # Never allow a state-file problem
            # to stop AURA.
            self.gemini_disabled = False

    # =====================================================
    # DISABLE GEMINI
    # =====================================================

    def _disable_gemini(
        self,
        reason: str
    ):

        today = (
            date.today().isoformat()
        )

        self.gemini_disabled = True
        self.disable_reason = reason
        self.disabled_date = today

        state = {
            "gemini_disabled": True,
            "disabled_date": today,
            "reason": reason
        }

        try:

            self.STATE_FILE.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with self.STATE_FILE.open(
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    state,
                    file,
                    indent=2
                )

        except Exception as error:

            print(
                "Unable to persist Gemini "
                f"circuit-breaker state: {error}"
            )

    # =====================================================
    # CHECK DISABLED STATE
    # =====================================================

    def _gemini_is_disabled_today(
        self
    ) -> bool:

        if not self.gemini_disabled:

            return False

        if (
            self.disabled_date ==
            date.today().isoformat()
        ):

            return True

        # New day → automatically allow Gemini again.
        self.gemini_disabled = False
        self.disable_reason = None
        self.disabled_date = None

        try:

            if self.STATE_FILE.exists():

                self.STATE_FILE.unlink()

        except Exception:
            pass

        return False


llm_planner = LLMPlanner()