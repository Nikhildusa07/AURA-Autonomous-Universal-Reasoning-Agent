from backend.app.core.human_intervention import (
    human_intervention
)
from backend.app.core.intervention_policy import (
    intervention_policy
)


class InterventionManager:

    def check_task(
        self,
        task_id: int,
        task_description: str,
        execution_id: str | None = None
    ) -> dict:

        policy_result = (
            intervention_policy.evaluate(
                task_description
            )
        )

        if not policy_result[
            "requires_intervention"
        ]:

            return {
                "required": False,
                "task_id": task_id,
                "task_description":
                    task_description,
                "execution_id":
                    execution_id,
                "status": "not_required",
                "policy": policy_result
            }

        intervention_request = (
            human_intervention.request_approval(
                task_id=task_id,
                task_description=task_description,
                reason=policy_result["reason"],
                category=policy_result["category"],
                execution_id=execution_id
            )
        )

        return {
            "required": True,
            "task_id": task_id,
            "task_description":
                task_description,
            "execution_id":
                execution_id,
            "status": "pending",
            "category":
                policy_result["category"],
            "matched_categories":
                policy_result[
                    "matched_categories"
                ],
            "reason":
                policy_result["reason"],
            "policy": policy_result,
            "intervention":
                intervention_request
        }

    def get_pending(self) -> list[dict]:

        return (
            human_intervention
            .get_pending_requests()
        )

    def get_all(self) -> list[dict]:

        return (
            human_intervention
            .get_all_requests()
        )

    def get_execution_requests(
        self,
        execution_id: str
    ) -> list[dict]:

        return (
            human_intervention
            .get_execution_requests(
                execution_id
            )
        )

    def approve(
        self,
        task_id: int,
        response: str = "Approved by human."
    ) -> dict:

        return human_intervention.respond(
            task_id=task_id,
            response=response
        )

    def reject(
        self,
        task_id: int,
        response: str = "Rejected by human."
    ) -> dict:

        return human_intervention.reject(
            task_id=task_id,
            response=response
        )


intervention_manager = InterventionManager()