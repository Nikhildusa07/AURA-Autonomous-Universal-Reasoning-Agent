import ast
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.core.planner import Planner
from backend.app.core.context_aware_executor import (
    context_aware_executor
)
from backend.app.core.evaluator import evaluator
from backend.app.core.replanner import replanner
from backend.app.core.uncertainty import uncertainty_engine
from backend.app.core.reflection import reflection_engine
from backend.app.core.verifier import verifier
from backend.app.core.result_generator import result_generator
from backend.app.core.context import context_manager
from backend.app.core.trace import trace
from backend.app.core.retry_manager import retry_manager
from backend.app.core.intervention_manager import (
    intervention_manager
)
from backend.app.memory.memory import memory
from backend.app.memory.execution_memory import (
    execution_memory
)
from backend.app.memory.semantic_learning import (
    semantic_learning
)


router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


class AgentRequest(BaseModel):
    goal: str


planner = Planner()


# =========================================================
# TASK SERIALIZATION
# =========================================================

def serialize_task(task):

    return {
        "id": task.id,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "parent_id": task.parent_id,
        "result": task.result,
        "error": task.error,
        "subtasks": [
            serialize_task(subtask)
            for subtask in task.subtasks
        ]
    }


# =========================================================
# PRIORITY ORDERING
# =========================================================

def order_tasks_by_priority(tasks):

    return sorted(
        tasks,
        key=lambda task: (
            task.priority,
            task.id
        )
    )


# =========================================================
# PERSIST EXECUTION STATE
# =========================================================

def persist_execution_state(
    execution_id: str,
    goal: str,
    tasks=None,
    status=None,
    result=None
):

    context = context_manager.get_context()

    serialized_tasks = None

    if tasks is not None:

        serialized_tasks = [
            serialize_task(task)
            for task in tasks
        ]

    return execution_memory.update_execution(
        execution_id=execution_id,
        status=status,
        context=context,
        result=result,
        tasks=serialized_tasks
    )


# =========================================================
# SYNCHRONIZE TASK WITH CONTEXT
# =========================================================

def synchronize_task_context(task):

    serialized_task = serialize_task(
        task
    )

    context_manager.update_task(
        task_id=task.id,
        task=serialized_task
    )

    if task.status == "completed":

        context_manager.add_completed_task(
            serialized_task
        )

    elif task.status == "failed":

        context_manager.add_failed_task(
            serialized_task
        )

    return serialized_task


# =========================================================
# PARSE SERIALIZED VALUE
# =========================================================

def parse_value(value):

    if isinstance(value, (dict, list)):
        return value

    if not isinstance(value, str):
        return value

    text = value.strip()

    if not text:
        return value

    try:
        return ast.literal_eval(text)
    except Exception:
        return value


# =========================================================
# NORMALIZE NESTED VALUE
# =========================================================

def normalize_value(value, depth=0):

    if depth > 10:
        return value

    value = parse_value(value)

    if isinstance(value, dict):

        return {
            key: normalize_value(
                item,
                depth + 1
            )
            for key, item in value.items()
        }

    if isinstance(value, list):

        return [
            normalize_value(
                item,
                depth + 1
            )
            for item in value
        ]

    return value


# =========================================================
# EXTRACT CALCULATOR RESULT
# =========================================================

def extract_calculation(value, depth=0):

    if depth > 10:
        return None

    value = parse_value(value)

    if isinstance(value, dict):

        tool = value.get("tool")

        expression = value.get(
            "expression"
        )

        result = value.get(
            "result"
        )

        # -------------------------------------------------
        # Direct calculator result
        # -------------------------------------------------

        if (
            tool == "calculator"
            and expression is not None
            and result is not None
        ):

            result = parse_value(result)

            # ---------------------------------------------
            # IMPORTANT FIX
            #
            # Sometimes calculator returns:
            #
            # {
            #   "tool": "calculator",
            #   "expression": "2500 * 3",
            #   "result": {
            #       "success": True,
            #       "expression": "2500 * 3",
            #       "result": 7500
            #   }
            # }
            #
            # Extract the INNER result.
            # ---------------------------------------------

            if isinstance(result, dict):

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
                            inner_result
                    }

            return {
                "type":
                    "calculation",

                "expression":
                    expression,

                "result":
                    result
            }

        # -------------------------------------------------
        # Calculator-like dictionary
        # -------------------------------------------------

        if (
            expression is not None
            and result is not None
        ):

            result = parse_value(result)

            if isinstance(result, dict):

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
                            inner_result
                    }

            return {
                "type":
                    "calculation",

                "expression":
                    expression,

                "result":
                    result
            }

        # -------------------------------------------------
        # Search nested values
        # -------------------------------------------------

        for item in value.values():

            found = extract_calculation(
                item,
                depth + 1
            )

            if found:
                return found

    elif isinstance(value, list):

        for item in value:

            found = extract_calculation(
                item,
                depth + 1
            )

            if found:
                return found

    elif isinstance(value, str):

        parsed = parse_value(value)

        if parsed != value:

            return extract_calculation(
                parsed,
                depth + 1
            )

    return None


# =========================================================
# EXTRACT RESEARCH RESULT
# =========================================================

def extract_research(value, depth=0):

    if depth > 10:
        return None

    value = parse_value(value)

    if isinstance(value, dict):

        if value.get("tool") == "web_research":

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
                    )
            }

        for item in value.values():

            found = extract_research(
                item,
                depth + 1
            )

            if found:
                return found

    elif isinstance(value, list):

        for item in value:

            found = extract_research(
                item,
                depth + 1
            )

            if found:
                return found

    elif isinstance(value, str):

        parsed = parse_value(value)

        if parsed != value:

            return extract_research(
                parsed,
                depth + 1
            )

    return None


# =========================================================
# EXTRACT BROWSER RESULT
# =========================================================

def extract_browser(value, depth=0):

    if depth > 10:
        return None

    value = parse_value(value)

    if isinstance(value, dict):

        if value.get("tool") in (
            "browser",
            "computer"
        ):

            return {
                "type":
                    value.get("tool"),

                "url":
                    value.get("url"),

                "title":
                    value.get("title"),

                "text":
                    value.get("text")
            }

        for item in value.values():

            found = extract_browser(
                item,
                depth + 1
            )

            if found:
                return found

    elif isinstance(value, list):

        for item in value:

            found = extract_browser(
                item,
                depth + 1
            )

            if found:
                return found

    elif isinstance(value, str):

        parsed = parse_value(value)

        if parsed != value:

            return extract_browser(
                parsed,
                depth + 1
            )

    return None


# =========================================================
# EXTRACT RESULT FROM TASK
# =========================================================

def extract_task_result(task):

    raw_result = getattr(
        task,
        "result",
        None
    )

    calculation = extract_calculation(
        raw_result
    )

    if calculation:
        return calculation

    research = extract_research(
        raw_result
    )

    if research:
        return research

    browser = extract_browser(
        raw_result
    )

    if browser:
        return browser

    for subtask in getattr(
        task,
        "subtasks",
        []
    ):

        found = extract_task_result(
            subtask
        )

        if found:
            return found

    return None


# =========================================================
# BUILD FINAL RESULT
# =========================================================

def build_final_result(
    goal,
    tasks,
    existing_result
):

    if not isinstance(
        existing_result,
        dict
    ):

        existing_result = {}

    calculations = []
    research_items = []
    browser_items = []

    # =====================================================
    # COLLECT ALL RESULTS
    # =====================================================

    for task in tasks:

        candidates = [
            task
        ]

        candidates.extend(
            getattr(
                task,
                "subtasks",
                []
            )
        )

        for item in candidates:

            if getattr(
                item,
                "status",
                None
            ) != "completed":

                continue

            raw_result = getattr(
                item,
                "result",
                None
            )

            calculation = extract_calculation(
                raw_result
            )

            if calculation:

                calculations.append(
                    calculation
                )

                continue

            research = extract_research(
                raw_result
            )

            if research:

                research_items.append(
                    research
                )

                continue

            browser = extract_browser(
                raw_result
            )

            if browser:

                browser_items.append(
                    browser
                )

    # =====================================================
    # CALCULATION
    # =====================================================

    if calculations:

        calculation = calculations[-1]

        expression = calculation.get(
            "expression"
        )

        result = calculation.get(
            "result"
        )

        if expression is None:

            expression = goal

        answer = (
            f"{expression} = {result}"
        )

        existing_result.update(
            {
                "goal":
                    goal,

                "status":
                    "completed",

                "answer":
                    answer,

                "summary":
                    answer,

                "key_results": [
                    {
                        "type":
                            "calculation",

                        "expression":
                            expression,

                        "result":
                            result
                    }
                ],

                "extracted_results": [
                    calculation
                ]
            }
        )

        return existing_result

    # =====================================================
    # RESEARCH
    # =====================================================

    if research_items:

        research = research_items[-1]

        query = research.get(
            "query"
        )

        results = research.get(
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

        answer = "\n".join(
            lines
        )

        existing_result.update(
            {
                "goal":
                    goal,

                "answer":
                    answer,

                "summary":
                    answer,

                "key_results": [
                    {
                        "type":
                            "research",

                        "query":
                            query,

                        "result_count":
                            len(results)
                    }
                ],

                "extracted_results":
                    research_items
            }
        )

        return existing_result

    # =====================================================
    # BROWSER
    # =====================================================

    if browser_items:

        browser = browser_items[-1]

        answer = (
            browser.get("text")
            or
            browser.get("title")
            or
            browser.get("url")
            or
            "Browser interaction completed."
        )

        existing_result.update(
            {
                "goal":
                    goal,

                "answer":
                    str(answer),

                "summary":
                    str(answer),

                "key_results": [
                    {
                        "type":
                            browser.get(
                                "type"
                            ),

                        "title":
                            browser.get(
                                "title"
                            ),

                        "url":
                            browser.get(
                                "url"
                            )
                    }
                ]
            }
        )

        return existing_result

    # =====================================================
    # GENERIC FALLBACK
    # =====================================================

    existing_result[
        "goal"
    ] = goal

    if not existing_result.get(
        "answer"
    ):

        existing_result[
            "answer"
        ] = (
            existing_result.get(
                "summary"
            )
            or
            f"AURA completed the objective: {goal}"
        )

    return existing_result


# =========================================================
# EXECUTE SUBTASK
# =========================================================

def execute_subtask(
    subtask,
    execution_id: str
):

    trace.record(
        "subtask_execution_started",
        {
            "task_id":
                subtask.id,

            "description":
                subtask.description,

            "priority":
                subtask.priority,

            "execution_id":
                execution_id
        }
    )

    autonomous_result = (
        context_aware_executor.execute(
            task_id=
                subtask.id,

            task_description=
                subtask.description
        )
    )

    context_manager.add_tool_output(
        autonomous_result
    )

    execution_data = (
        autonomous_result.get(
            "execution",
            {}
        )
    )

    execution_data = normalize_value(
        execution_data
    )

    trace.record(
        "context_aware_execution_completed",
        {
            "task_id":
                subtask.id,

            "execution_id":
                execution_id,

            "priority":
                subtask.priority,

            "tool":
                (
                    execution_data.get(
                        "tool"
                    )
                    if isinstance(
                        execution_data,
                        dict
                    )
                    else None
                ),

            "execution_type":
                (
                    execution_data.get(
                        "execution_type"
                    )
                    if isinstance(
                        execution_data,
                        dict
                    )
                    else None
                ),

            "selection_method":
                (
                    execution_data.get(
                        "selection_method"
                    )
                    if isinstance(
                        execution_data,
                        dict
                    )
                    else None
                ),

            "success":
                autonomous_result.get(
                    "success"
                ),

            "context_used":
                bool(
                    autonomous_result.get(
                        "context_used"
                    )
                )
        }
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    if autonomous_result.get(
        "success"
    ):

        # Store the real dictionary instead of
        # converting it into a string.
        subtask.complete(
            execution_data
        )

    else:

        error_message = (
            autonomous_result.get(
                "error"
            )
        )

        if not error_message:

            if isinstance(
                execution_data,
                dict
            ):

                error_message = (
                    execution_data.get(
                        "error"
                    )
                )

        if not error_message:

            error_message = (
                "Autonomous execution failed."
            )

        subtask.fail(
            str(error_message)
        )

    synchronize_task_context(
        subtask
    )

    trace.record(
        "subtask_execution_completed",
        {
            "task_id":
                subtask.id,

            "execution_id":
                execution_id,

            "priority":
                subtask.priority,

            "status":
                subtask.status,

            "result":
                autonomous_result
        }
    )

    return autonomous_result


# =========================================================
# AGENT RUN
# =========================================================

@router.post("/run")
def run_agent(
    request: AgentRequest
):

    trace.clear()
    context_manager.reset()
    retry_manager.reset()
    context_aware_executor.clear_context()

    goal = request.goal.strip()

    if not goal:

        return {
            "success":
                False,

            "error":
                "Goal cannot be empty."
        }

    context_manager.set_goal(
        goal
    )

    trace.record(
        "goal_received",
        {
            "goal":
                goal
        }
    )

    # =====================================================
    # CREATE PLAN
    # =====================================================

    tasks = planner.create_plan(
        goal
    )

    for task in tasks:

        context_manager.add_task(
            serialize_task(task)
        )

    trace.record(
        "plan_created",
        {
            "task_count":
                len(tasks),

            "plan": [
                serialize_task(task)
                for task in tasks
            ]
        }
    )

    # =====================================================
    # CREATE EXECUTION
    # =====================================================

    execution_id = str(
        uuid.uuid4()
    )

    execution_memory.create_execution(
        execution_id=
            execution_id,

        goal=
            goal,

        tasks=[
            serialize_task(task)
            for task in tasks
        ],

        status=
            "in_progress"
    )

    # =====================================================
    # EXECUTE TASKS
    # =====================================================

    executed_tasks = []
    intervention_requests = []

    for task in tasks:

        if task.subtasks:

            ordered_subtasks = (
                order_tasks_by_priority(
                    task.subtasks
                )
            )

            trace.record(
                "priority_order_selected",
                {
                    "parent_task_id":
                        task.id,

                    "execution_order": [
                        {
                            "task_id":
                                subtask.id,

                            "priority":
                                subtask.priority,

                            "description":
                                subtask.description
                        }

                        for subtask
                        in ordered_subtasks
                    ]
                }
            )

            for subtask in ordered_subtasks:

                intervention_check = (
                    intervention_manager.check_task(
                        task_id=
                            subtask.id,

                        task_description=
                            subtask.description
                    )
                )

                trace.record(
                    "intervention_check",
                    intervention_check
                )

                if intervention_check[
                    "required"
                ]:

                    intervention_requests.append(
                        intervention_check
                    )

                    subtask.status = (
                        "pending"
                    )

                    synchronize_task_context(
                        subtask
                    )

                    persist_execution_state(
                        execution_id=
                            execution_id,

                        goal=
                            goal,

                        tasks=
                            tasks,

                        status=
                            "waiting_for_human"
                    )

                    continue

                execute_subtask(
                    subtask=
                        subtask,

                    execution_id=
                        execution_id
                )

                persist_execution_state(
                    execution_id=
                        execution_id,

                    goal=
                        goal,

                    tasks=
                        tasks,

                    status=
                        "in_progress"
                )

                while subtask.status == "failed":

                    retry_result = (
                        retry_manager.prepare_retry(
                            subtask
                        )
                    )

                    trace.record(
                        "retry_attempted",
                        retry_result
                    )

                    if not retry_result[
                        "retry"
                    ]:
                        break

                    execute_subtask(
                        subtask=
                            subtask,

                        execution_id=
                            execution_id
                    )

            failed_subtasks = [
                subtask
                for subtask
                in task.subtasks
                if subtask.status ==
                "failed"
            ]

            pending_subtasks = [
                subtask
                for subtask
                in task.subtasks
                if subtask.status ==
                "pending"
            ]

            if failed_subtasks:

                task.fail(
                    f"{len(failed_subtasks)} "
                    "subtask(s) failed after retry attempts."
                )

            elif pending_subtasks:

                task.status = "pending"

                task.result = (
                    "Task is waiting for human intervention."
                )

            else:

                task.complete(
                    "All subtasks completed successfully."
                )

            synchronize_task_context(
                task
            )

        else:

            intervention_check = (
                intervention_manager.check_task(
                    task_id=
                        task.id,

                    task_description=
                        task.description
                )
            )

            trace.record(
                "intervention_check",
                intervention_check
            )

            if intervention_check[
                "required"
            ]:

                intervention_requests.append(
                    intervention_check
                )

                task.status = "pending"

                synchronize_task_context(
                    task
                )

            else:

                execute_subtask(
                    subtask=
                        task,

                    execution_id=
                        execution_id
                )

                persist_execution_state(
                    execution_id=
                        execution_id,

                    goal=
                        goal,

                    tasks=
                        tasks,

                    status=
                        "in_progress"
                )

                while task.status == "failed":

                    retry_result = (
                        retry_manager.prepare_retry(
                            task
                        )
                    )

                    trace.record(
                        "retry_attempted",
                        retry_result
                    )

                    if not retry_result[
                        "retry"
                    ]:
                        break

                    execute_subtask(
                        subtask=
                            task,

                        execution_id=
                            execution_id
                    )

        synchronize_task_context(
            task
        )

        executed_tasks.append(
            task
        )

        persist_execution_state(
            execution_id=
                execution_id,

            goal=
                goal,

            tasks=
                tasks,

            status=
                "in_progress"
        )

    # =====================================================
    # HUMAN INTERVENTION
    # =====================================================

    if any(
        task.status == "pending"
        for task in executed_tasks
    ):

        execution_status = (
            "waiting_for_human"
        )

        pending_plan = [
            serialize_task(task)
            for task in executed_tasks
        ]

        pending_result = {
            "status":
                execution_status,

            "summary":
                "AURA paused execution because "
                "human intervention is required.",

            "execution_id":
                execution_id
        }

        memory.remember_episode(
            goal=
                goal,

            result=
                pending_plan,

            status=
                execution_status
        )

        final_state = (
            execution_memory.update_execution(
                execution_id=
                    execution_id,

                status=
                    execution_status,

                context=
                    context_manager.get_context(),

                result=
                    pending_result,

                tasks=
                    pending_plan
            )
        )

        return {
            "success":
                False,

            "execution_id":
                execution_id,

            "goal":
                goal,

            "status":
                execution_status,

            "final_result":
                pending_result,

            "task_count":
                len(pending_plan),

            "plan":
                pending_plan,

            "evaluations": [],
            "uncertainty": [],
            "reflections": [],
            "verification": [],
            "recovery": [],
            "replanning": [],

            "human_intervention": {
                "required":
                    True,

                "count":
                    len(
                        intervention_requests
                    ),

                "requests":
                    intervention_requests,

                "pending":
                    intervention_manager.get_pending()
            },

            "context": {
                "summary":
                    context_manager.get_summary(),

                "data":
                    context_manager.get_context()
            },

            "memory": {
                "episodes_stored":
                    len(
                        memory.get_episodes()
                    ),

                "semantic_memory_updated":
                    False
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

    # =====================================================
    # EVALUATION
    # =====================================================

    evaluations = [
        evaluator.evaluate_task(task)
        for task in executed_tasks
    ]

    for evaluation in evaluations:

        context_manager.add_evaluation(
            evaluation
        )

    trace.record(
        "evaluation_completed",
        evaluations
    )

    # =====================================================
    # UNCERTAINTY
    # =====================================================

    uncertainty = [
        uncertainty_engine.estimate(task)
        for task in executed_tasks
    ]

    trace.record(
        "uncertainty_estimated",
        uncertainty
    )

    # =====================================================
    # REFLECTION
    # =====================================================

    reflections = [
        reflection_engine.reflect(task)
        for task in executed_tasks
    ]

    for reflection in reflections:

        context_manager.add_reflection(
            reflection
        )

    trace.record(
        "self_reflection_completed",
        reflections
    )

    # =====================================================
    # RECOVERY / REPLANNING
    # =====================================================

    recovery_results = []
    replanning_results = []

    for task, evaluation in zip(
        executed_tasks,
        evaluations
    ):

        if not evaluation["success"]:

            replanning_result = (
                replanner.create_recovery_plan(
                    task
                )
            )

            replanning_results.append(
                replanning_result
            )

            recovery_results.append(
                {
                    "recovered":
                        False,

                    "task_id":
                        task.id,

                    "message":
                        "Retry limit reached. "
                        "Task requires human attention."
                }
            )

    # =====================================================
    # VERIFICATION
    # =====================================================

    verification = [
        verifier.verify(
            task,
            goal
        )
        for task in executed_tasks
    ]

    for verification_result in verification:

        context_manager.add_verification(
            verification_result
        )

    trace.record(
        "result_verification_completed",
        verification
    )

    # =====================================================
    # FINAL STATUS
    # =====================================================

    execution_status = (
        "completed"

        if (
            executed_tasks
            and all(
                task.status == "completed"
                for task in executed_tasks
            )
        )

        else
            "failed"
    )

    # =====================================================
    # PLAN
    # =====================================================

    plan = [
        serialize_task(task)
        for task in executed_tasks
    ]

    # =====================================================
    # EPISODIC MEMORY
    # =====================================================

    memory.remember_episode(
        goal=
            goal,

        result=
            plan,

        status=
            execution_status
    )

    context_manager.add_memory(
        {
            "type":
                "episodic",

            "goal":
                goal,

            "status":
                execution_status
        }
    )

    # =====================================================
    # SEMANTIC MEMORY
    # =====================================================

    semantic_learning_result = (
        semantic_learning.learn_from_execution(
            goal=
                goal,

            tasks=
                executed_tasks,

            status=
                execution_status
        )
    )

    context_manager.add_memory(
        {
            "type":
                "semantic",

            "learned":
                semantic_learning_result.get(
                    "learned",
                    0
                ),

            "facts":
                semantic_learning_result.get(
                    "facts",
                    []
                )
        }
    )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    generated_result = (
        result_generator.generate(
            goal=
                goal,

            tasks=
                executed_tasks
        )
    )

    final_result = build_final_result(
        goal=
            goal,

        tasks=
            executed_tasks,

        existing_result=
            generated_result
    )

    trace.record(
        "final_result_generated",
        final_result
    )

    # =====================================================
    # FINAL CONTEXT
    # =====================================================

    context_summary = (
        context_manager.get_summary()
    )

    trace.record(
        "context_updated",
        context_summary
    )

    trace.record(
        "execution_finished",
        {
            "status":
                execution_status,

            "execution_id":
                execution_id
        }
    )

    # =====================================================
    # PERSIST FINAL STATE
    # =====================================================

    execution_record = (
        execution_memory.update_execution(
            execution_id=
                execution_id,

            status=
                execution_status,

            context=
                context_manager.get_context(),

            result=
                final_result,

            tasks=
                plan
        )
    )

    trace.record(
        "execution_state_persisted",
        {
            "execution_id":
                execution_id,

            "status":
                execution_status
        }
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "success":
            execution_status == "completed",

        "execution_id":
            execution_id,

        "goal":
            goal,

        "status":
            execution_status,

        "final_result":
            final_result,

        "task_count":
            len(plan),

        "plan":
            plan,

        "evaluations":
            evaluations,

        "uncertainty":
            uncertainty,

        "reflections":
            reflections,

        "verification":
            verification,

        "recovery":
            recovery_results,

        "replanning":
            replanning_results,

        "human_intervention": {
            "required":
                len(
                    intervention_requests
                ) > 0,

            "count":
                len(
                    intervention_requests
                ),

            "requests":
                intervention_requests,

            "pending":
                intervention_manager.get_pending()
        },

        "context": {
            "summary":
                context_summary,

            "data":
                context_manager.get_context()
        },

        "memory": {
            "episodes_stored":
                len(
                    memory.get_episodes()
                ),

            "semantic_memory_updated":
                semantic_learning_result.get(
                    "success",
                    False
                ),

            "semantic_facts_learned":
                semantic_learning_result.get(
                    "learned",
                    0
                ),

            "semantic_facts":
                semantic_learning_result.get(
                    "facts",
                    []
                )
        },

        "execution_state": {
            "persisted":
                execution_record is not None,

            "execution_id":
                execution_id,

            "status":
                execution_status
        },

        "execution_trace":
            trace.get_events()
    }