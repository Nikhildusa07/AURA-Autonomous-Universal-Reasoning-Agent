from typing import Any

from backend.app.core.autonomous_executor import (
    autonomous_executor
)
from backend.app.core.context_aware_executor import (
    context_aware_executor
)
from backend.app.core.evaluator import evaluator
from backend.app.core.reflection import reflection_engine
from backend.app.core.uncertainty import uncertainty_engine
from backend.app.core.verifier import verifier
from backend.app.core.result_generator import result_generator
from backend.app.core.context import context_manager
from backend.app.core.trace import trace
from backend.app.core.retry_manager import retry_manager
from backend.app.core.learning import learning_engine
from backend.app.core.replanner import replanner
from backend.app.memory.memory import memory
from backend.app.memory.execution_memory import (
    execution_memory
)
from backend.app.memory.intervention_memory import (
    intervention_memory
)


class InterventionResume:

    def _find_execution(
        self,
        task_id: int
    ) -> dict | None:

        request = (
            intervention_memory
            .get_request_by_task_id(
                task_id
            )
        )

        if request is None:
            return None

        execution_id = request.get(
            "execution_id"
        )

        if not execution_id:
            return None

        return execution_memory.get_execution(
            execution_id
        )

    def _find_task(
        self,
        tasks: list[dict],
        task_id: int
    ) -> dict | None:

        for task in tasks:

            if not isinstance(task, dict):
                continue

            if task.get("id") == task_id:
                return task

            for subtask in task.get(
                "subtasks",
                []
            ):

                if (
                    isinstance(subtask, dict)
                    and subtask.get("id") == task_id
                ):
                    return subtask

        return None

    def _update_task(
        self,
        tasks: list[dict],
        task_id: int,
        task_data: dict
    ) -> bool:

        for index, task in enumerate(tasks):

            if not isinstance(task, dict):
                continue

            if task.get("id") == task_id:

                tasks[index] = {
                    **task,
                    **task_data
                }

                return True

            subtasks = task.get(
                "subtasks",
                []
            )

            for sub_index, subtask in enumerate(
                subtasks
            ):

                if (
                    isinstance(subtask, dict)
                    and subtask.get("id") == task_id
                ):

                    subtasks[sub_index] = {
                        **subtask,
                        **task_data
                    }

                    tasks[index]["subtasks"] = subtasks

                    return True

        return False

    def _has_pending_tasks(
        self,
        tasks: list[dict]
    ) -> bool:

        for task in tasks:

            if task.get("status") == "pending":
                return True

            for subtask in task.get(
                "subtasks",
                []
            ):

                if (
                    isinstance(subtask, dict)
                    and subtask.get("status") == "pending"
                ):
                    return True

        return False

    def _all_completed(
        self,
        tasks: list[dict]
    ) -> bool:

        if not tasks:
            return False

        for task in tasks:

            if task.get("status") != "completed":
                return False

        return True

    def resume(
        self,
        task_id: int,
        task_description: str
    ) -> dict:

        # -----------------------------------------------------
        # 1. FIND INTERVENTION REQUEST
        # -----------------------------------------------------

        request = (
            intervention_memory
            .get_request_by_task_id(
                task_id
            )
        )

        if request is None:

            return {
                "success": False,
                "task_id": task_id,
                "status": "not_found",
                "error":
                    "Human intervention request was not found."
            }

        # -----------------------------------------------------
        # 2. CHECK APPROVAL
        # -----------------------------------------------------

        if request["status"] != "approved":

            return {
                "success": False,
                "task_id": task_id,
                "execution_id":
                    request.get(
                        "execution_id"
                    ),
                "status":
                    request["status"],
                "error": (
                    "Task cannot be resumed because "
                    "human approval has not been granted."
                )
            }

        execution_id = request.get(
            "execution_id"
        )

        if not execution_id:

            return {
                "success": False,
                "task_id": task_id,
                "status": "missing_execution",
                "error": (
                    "The intervention request is not "
                    "associated with an execution."
                )
            }

        # -----------------------------------------------------
        # 3. LOAD SAME PERSISTED EXECUTION
        # -----------------------------------------------------

        execution = (
            execution_memory.get_execution(
                execution_id
            )
        )

        if execution is None:

            return {
                "success": False,
                "task_id": task_id,
                "execution_id": execution_id,
                "status": "execution_not_found",
                "error": (
                    "The persisted AURA execution "
                    "could not be found."
                )
            }

        if execution["status"] not in (
            "waiting_for_human",
            "in_progress"
        ):

            return {
                "success": False,
                "task_id": task_id,
                "execution_id": execution_id,
                "status": execution["status"],
                "error": (
                    "This execution is not in a "
                    "resumable state."
                )
            }

        goal = execution["goal"]

        tasks = execution.get(
            "tasks",
            []
        )

        context_data = execution.get(
            "context",
            {}
        )

        # -----------------------------------------------------
        # 4. RESTORE CONTEXT
        # -----------------------------------------------------

        context_manager.reset()

        context_manager.set_goal(
            goal
        )

        if isinstance(context_data, dict):

            for task in context_data.get(
                "completed_tasks",
                []
            ):

                context_manager.add_completed_task(
                    task
                )

            for task in context_data.get(
                "failed_tasks",
                []
            ):

                context_manager.add_failed_task(
                    task
                )

            for task in context_data.get(
                "tasks",
                []
            ):

                context_manager.add_task(
                    task
                )

            for item in context_data.get(
                "tool_outputs",
                []
            ):

                context_manager.add_tool_output(
                    item
                )

        context_aware_executor.clear_context()

        # -----------------------------------------------------
        # 5. RESTORE PREVIOUS TASK RESULTS
        # -----------------------------------------------------

        for task in tasks:

            if not isinstance(task, dict):
                continue

            status = task.get(
                "status"
            )

            if status != "completed":
                continue

            result = task.get(
                "result"
            )

            context_aware_executor.context.store(
                task_id=task.get("id"),
                task_description=task.get(
                    "description",
                    ""
                ),
                result=result,
                success=True
            )

            for subtask in task.get(
                "subtasks",
                []
            ):

                if (
                    not isinstance(subtask, dict)
                    or subtask.get("status") != "completed"
                ):
                    continue

                context_aware_executor.context.store(
                    task_id=subtask.get("id"),
                    task_description=subtask.get(
                        "description",
                        ""
                    ),
                    result=subtask.get(
                        "result"
                    ),
                    success=True
                )

        # -----------------------------------------------------
        # 6. FIND APPROVED TASK
        # -----------------------------------------------------

        target_task = self._find_task(
            tasks=tasks,
            task_id=task_id
        )

        if target_task is None:

            return {
                "success": False,
                "task_id": task_id,
                "execution_id": execution_id,
                "status": "task_not_found",
                "error": (
                    "The task could not be found "
                    "inside the persisted execution."
                )
            }

        # Use persisted description unless the caller supplied
        # a non-empty description.
        description = (
            task_description.strip()
            if task_description
            else target_task.get(
                "description",
                ""
            )
        )

        # -----------------------------------------------------
        # 7. EXECUTE APPROVED TASK
        # -----------------------------------------------------

        trace.clear()

        trace.record(
            "execution_resumed",
            {
                "execution_id": execution_id,
                "task_id": task_id
            }
        )

        execution_result = (
            context_aware_executor.execute(
                task_id=task_id,
                task_description=description
            )
        )

        # -----------------------------------------------------
        # 8. UPDATE TASK
        # -----------------------------------------------------

        if execution_result["success"]:

            updated_task_data = {
                "status": "completed",
                "result": str(
                    execution_result["execution"]
                ),
                "error": None
            }

        else:

            updated_task_data = {
                "status": "failed",
                "result": None,
                "error":
                    execution_result.get(
                        "execution",
                        {}
                    ).get(
                        "error",
                        "Resumed task failed."
                    )
            }

        self._update_task(
            tasks=tasks,
            task_id=task_id,
            task_data=updated_task_data
        )

        # -----------------------------------------------------
        # 9. UPDATE PERSISTED TASK
        # -----------------------------------------------------

        execution_memory.update_execution(
            execution_id=execution_id,
            tasks=tasks,
            context=context_manager.get_context(),
            status="in_progress"
        )

        trace.record(
            "resumed_task_completed",
            {
                "execution_id": execution_id,
                "task_id": task_id,
                "status":
                    updated_task_data["status"]
            }
        )

        # -----------------------------------------------------
        # 10. IF RESUMED TASK FAILED, STOP HERE
        # -----------------------------------------------------

        if not execution_result["success"]:

            retry_manager.reset()

            retry_result = (
                retry_manager.prepare_retry(
                    type(
                        "ResumeTask",
                        (),
                        {
                            "id": task_id,
                            "status": "failed",
                            "result": None,
                            "error":
                                updated_task_data[
                                    "error"
                                ]
                        }
                    )()
                )
            )

            trace.record(
                "resume_failure",
                retry_result
            )

            execution_memory.update_execution(
                execution_id=execution_id,
                tasks=tasks,
                context=context_manager.get_context(),
                result={
                    "status": "failed",
                    "task_id": task_id,
                    "error":
                        updated_task_data[
                            "error"
                        ]
                },
                status="failed"
            )

            return {
                "success": False,
                "task_id": task_id,
                "execution_id": execution_id,
                "status": "failed",
                "execution": execution_result,
                "retry": retry_result,
                "execution_state":
                    execution_memory.get_execution(
                        execution_id
                    ),
                "execution_trace":
                    trace.get_events()
            }

        # -----------------------------------------------------
        # 11. CHECK WHETHER OTHER TASKS REMAIN
        # -----------------------------------------------------

        pending_tasks = []

        for task in tasks:

            if task.get("status") == "pending":

                pending_tasks.append(task)

            for subtask in task.get(
                "subtasks",
                []
            ):

                if (
                    isinstance(subtask, dict)
                    and subtask.get("status") == "pending"
                ):

                    pending_tasks.append(
                        subtask
                    )

        # -----------------------------------------------------
        # 12. STILL WAITING FOR HUMAN TASKS
        # -----------------------------------------------------

        if pending_tasks:

            execution_memory.update_execution(
                execution_id=execution_id,
                tasks=tasks,
                context=context_manager.get_context(),
                status="waiting_for_human"
            )

            return {
                "success": True,
                "task_id": task_id,
                "execution_id": execution_id,
                "status": "waiting_for_human",
                "message": (
                    "Approved task completed. "
                    "Other tasks are still pending."
                ),
                "execution": execution_result,
                "remaining_tasks": pending_tasks,
                "execution_state":
                    execution_memory.get_execution(
                        execution_id
                    ),
                "execution_trace":
                    trace.get_events()
            }

        # -----------------------------------------------------
        # 13. EVALUATION OF COMPLETE EXECUTION
        # -----------------------------------------------------

        task_objects = []

        # The persisted representation does not contain live
        # Task objects, so evaluate the resumed execution using
        # the completed execution records.
        for task in tasks:

            if task.get("status") == "completed":

                task_objects.append(
                    type(
                        "PersistedTask",
                        (),
                        {
                            "id":
                                task.get("id"),
                            "description":
                                task.get(
                                    "description",
                                    ""
                                ),
                            "status":
                                task.get(
                                    "status"
                                ),
                            "priority":
                                task.get(
                                    "priority",
                                    1
                                ),
                            "parent_id":
                                task.get(
                                    "parent_id"
                                ),
                            "result":
                                task.get(
                                    "result"
                                ),
                            "error":
                                task.get(
                                    "error"
                                ),
                            "subtasks": []
                        }
                    )()
                )

        evaluations = [
            evaluator.evaluate_task(
                task
            )
            for task in task_objects
        ]

        uncertainty = [
            uncertainty_engine.estimate(
                task
            )
            for task in task_objects
        ]

        reflections = [
            reflection_engine.reflect(
                task
            )
            for task in task_objects
        ]

        verification = [
            verifier.verify(
                task,
                goal
            )
            for task in task_objects
        ]

        # -----------------------------------------------------
        # 14. FINAL STATUS
        # -----------------------------------------------------

        execution_status = (
            "completed"
            if (
                self._all_completed(tasks)
                and all(
                    evaluation.get(
                        "success",
                        False
                    )
                    for evaluation in evaluations
                )
            )
            else "failed"
        )

        # -----------------------------------------------------
        # 15. FINAL RESULT
        # -----------------------------------------------------

        final_result = result_generator.generate(
            goal=goal,
            tasks=task_objects
        )

        # -----------------------------------------------------
        # 16. MEMORY
        # -----------------------------------------------------

        memory.remember_episode(
            goal=goal,
            result=tasks,
            status=execution_status
        )

        learning_result = learning_engine.learn(
            key="last_goal",
            value=goal
        )

        # -----------------------------------------------------
        # 17. PERSIST FINAL STATE
        # -----------------------------------------------------

        final_state = (
            execution_memory.update_execution(
                execution_id=execution_id,
                status=execution_status,
                context=context_manager.get_context(),
                result=final_result,
                tasks=tasks
            )
        )

        trace.record(
            "execution_resumed_and_finished",
            {
                "execution_id": execution_id,
                "status": execution_status
            }
        )

        return {
            "success":
                execution_status == "completed",
            "task_id": task_id,
            "execution_id":
                execution_id,
            "goal": goal,
            "status":
                execution_status,
            "human_approval": {
                "status":
                    request["status"],
                "response":
                    request["response"]
            },
            "execution":
                execution_result,
            "evaluations":
                evaluations,
            "uncertainty":
                uncertainty,
            "reflections":
                reflections,
            "verification":
                verification,
            "final_result":
                final_result,
            "memory": {
                "episode_stored": True,
                "semantic_memory_updated":
                    learning_result.get(
                        "success",
                        False
                    )
            },
            "execution_state": {
                "persisted":
                    final_state is not None,
                "execution_id":
                    execution_id,
                "status":
                    execution_status
            },
            "execution_trace":
                trace.get_events()
        }


intervention_resume = InterventionResume()