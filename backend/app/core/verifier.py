from backend.app.models.task import Task


class VerificationEngine:

    def verify(self, task: Task, goal: str) -> dict:
        issues = []

        if task.status != "completed":
            issues.append("Task was not completed.")

        if task.subtasks:
            failed_subtasks = [
                subtask
                for subtask in task.subtasks
                if subtask.status != "completed"
            ]

            if failed_subtasks:
                issues.append(
                    f"{len(failed_subtasks)} subtask(s) were not completed."
                )

        if task.result is None:
            issues.append("Task did not produce a result.")

        verified = len(issues) == 0

        return {
            "verified": verified,
            "task_id": task.id,
            "goal": goal,
            "status": task.status,
            "issues": issues,
            "verification_message": (
                "Result passed basic verification."
                if verified
                else "Result failed verification."
            )
        }


verifier = VerificationEngine()