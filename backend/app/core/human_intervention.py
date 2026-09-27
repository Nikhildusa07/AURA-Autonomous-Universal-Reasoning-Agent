from typing import Optional

from backend.app.memory.intervention_memory import (
    intervention_memory
)


class HumanIntervention:

    def request_approval(
        self,
        task_id: int,
        task_description: str,
        reason: str,
        category: Optional[str] = None,
        execution_id: Optional[str] = None
    ) -> dict:

        existing_request = (
            intervention_memory.get_request_by_task_id(
                task_id
            )
        )

        if existing_request is not None:

            if existing_request["status"] == "pending":

                return {
                    "required": True,
                    "task_id": task_id,
                    "task_description":
                        task_description,
                    "reason": reason,
                    "status": "pending",
                    "category":
                        existing_request["category"],
                    "execution_id":
                        existing_request["execution_id"]
                }

        request = intervention_memory.create_request(
            task_id=task_id,
            task_description=task_description,
            reason=reason,
            category=category,
            execution_id=execution_id
        )

        return {
            "required": True,
            "task_id": task_id,
            "task_description":
                task_description,
            "reason": reason,
            "status":
                request["status"],
            "category":
                request["category"],
            "execution_id":
                request["execution_id"]
        }

    def respond(
        self,
        task_id: int,
        response: str
    ) -> dict:

        request = (
            intervention_memory
            .get_request_by_task_id(task_id)
        )

        if request is None:

            return {
                "success": False,
                "task_id": task_id,
                "error":
                    "Intervention request not found."
            }

        if request["status"] != "pending":

            return {
                "success": False,
                "task_id": task_id,
                "status":
                    request["status"],
                "error":
                    "Intervention request is no longer pending."
            }

        updated_request = (
            intervention_memory.update_status(
                task_id=task_id,
                status="approved",
                response=response
            )
        )

        return {
            "success": True,
            "task_id": task_id,
            "execution_id":
                updated_request["execution_id"],
            "status":
                updated_request["status"],
            "response":
                updated_request["response"]
        }

    def reject(
        self,
        task_id: int,
        response: str = "Task rejected by human."
    ) -> dict:

        request = (
            intervention_memory
            .get_request_by_task_id(task_id)
        )

        if request is None:

            return {
                "success": False,
                "task_id": task_id,
                "error":
                    "Intervention request not found."
            }

        if request["status"] != "pending":

            return {
                "success": False,
                "task_id": task_id,
                "status":
                    request["status"],
                "error":
                    "Intervention request is no longer pending."
            }

        updated_request = (
            intervention_memory.update_status(
                task_id=task_id,
                status="rejected",
                response=response
            )
        )

        return {
            "success": True,
            "task_id": task_id,
            "execution_id":
                updated_request["execution_id"],
            "status":
                updated_request["status"],
            "response":
                updated_request["response"]
        }

    def get_pending_requests(
        self
    ) -> list[dict]:

        return (
            intervention_memory
            .get_pending_requests()
        )

    def get_all_requests(
        self
    ) -> list[dict]:

        return (
            intervention_memory
            .get_all_requests()
        )

    def get_execution_requests(
        self,
        execution_id: str
    ) -> list[dict]:

        return (
            intervention_memory
            .get_requests_by_execution_id(
                execution_id
            )
        )


human_intervention = HumanIntervention()