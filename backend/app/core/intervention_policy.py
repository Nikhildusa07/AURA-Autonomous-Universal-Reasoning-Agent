import re
from typing import Any


class InterventionPolicy:

    def __init__(self):
        self.rules = {
            "destructive": [
                "delete",
                "remove",
                "drop database",
                "destroy",
                "wipe",
                "erase"
            ],
            "production": [
                "deploy",
                "production deployment",
                "production release",
                "release to production",
                "publish to production"
            ],
            "external_action": [
                "send email",
                "send an email",
                "email the",
                "send message",
                "send a message",
                "post",
                "submit",
                "purchase",
                "buy"
            ],
            "sensitive": [
                "password",
                "api key",
                "secret",
                "credential",
                "token"
            ]
        }

    def _contains_keyword(
        self,
        description: str,
        keyword: str
    ) -> bool:

        keyword = keyword.lower().strip()

        if not keyword:
            return False

        if " " in keyword:
            return keyword in description

        return bool(
            re.search(
                rf"\b{re.escape(keyword)}\b",
                description
            )
        )

    def requires_intervention(
        self,
        task_description: str
    ) -> dict:

        description = task_description.lower().strip()

        if not description:
            return {
                "required": False,
                "category": None,
                "reason": None,
                "matched_categories": []
            }

        matched_categories = []

        # --------------------------------------------------
        # DESTRUCTIVE OPERATIONS
        # --------------------------------------------------

        for keyword in self.rules["destructive"]:

            if self._contains_keyword(
                description,
                keyword
            ):
                matched_categories.append(
                    "destructive"
                )
                break

        # --------------------------------------------------
        # PRODUCTION OPERATIONS
        # --------------------------------------------------

        production_required = False

        if self._contains_keyword(
            description,
            "deploy"
        ):
            production_required = True

        production_phrases = [
            "production deployment",
            "production release",
            "release to production",
            "publish to production"
        ]

        for phrase in production_phrases:

            if self._contains_keyword(
                description,
                phrase
            ):
                production_required = True
                break

        if production_required:
            matched_categories.append(
                "production"
            )

        # --------------------------------------------------
        # EXTERNAL ACTIONS
        # --------------------------------------------------

        for keyword in self.rules["external_action"]:

            if self._contains_keyword(
                description,
                keyword
            ):
                matched_categories.append(
                    "external_action"
                )
                break

        # --------------------------------------------------
        # SENSITIVE INFORMATION
        # --------------------------------------------------

        for keyword in self.rules["sensitive"]:

            if self._contains_keyword(
                description,
                keyword
            ):
                matched_categories.append(
                    "sensitive"
                )
                break

        matched_categories = list(
            dict.fromkeys(
                matched_categories
            )
        )

        if not matched_categories:
            return {
                "required": False,
                "category": None,
                "reason": None,
                "matched_categories": []
            }

        category = matched_categories[0]

        reasons = {
            "destructive": (
                "The task appears to perform a "
                "potentially destructive operation."
            ),
            "production": (
                "The task appears to perform an "
                "operation affecting a production environment."
            ),
            "external_action": (
                "The task appears to perform an "
                "external action on behalf of the user."
            ),
            "sensitive": (
                "The task appears to involve "
                "sensitive credentials or secrets."
            )
        }

        return {
            "required": True,
            "category": category,
            "matched_categories": matched_categories,
            "reason": reasons[category]
        }

    def evaluate(
        self,
        task_description: str,
        task_context: Any = None
    ) -> dict:

        policy_result = self.requires_intervention(
            task_description
        )

        return {
            "task": task_description,
            "requires_intervention":
                policy_result["required"],
            "category":
                policy_result["category"],
            "matched_categories":
                policy_result.get(
                    "matched_categories",
                    []
                ),
            "reason":
                policy_result["reason"],
            "context_provided":
                task_context is not None
        }


intervention_policy = InterventionPolicy()