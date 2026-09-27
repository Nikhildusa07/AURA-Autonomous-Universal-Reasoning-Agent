from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


# =========================================================
# EVALUATION RECORD
# =========================================================

@dataclass
class EvaluationRecord:
    """
    Stores the measurable results of one benchmark execution.
    """

    benchmark_id: str

    success: bool = False

    total_tasks: int = 0
    completed_tasks: int = 0

    expected_tools: list[str] = field(
        default_factory=list
    )

    actual_tools: list[str] = field(
        default_factory=list
    )

    tool_selection_correct: bool = False

    verification_expected: bool = False
    verification_success: bool = False

    recovery_expected: bool = False
    recovery_success: bool = False

    execution_latency_ms: float = 0.0

    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    error: Optional[str] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:

        task_completion_rate = (
            (
                self.completed_tasks
                / self.total_tasks
            )
            * 100
            if self.total_tasks > 0
            else 0.0
        )

        return {
            "benchmark_id":
                self.benchmark_id,

            "success":
                self.success,

            "total_tasks":
                self.total_tasks,

            "completed_tasks":
                self.completed_tasks,

            "task_completion_rate":
                round(
                    task_completion_rate,
                    2
                ),

            "expected_tools":
                self.expected_tools,

            "actual_tools":
                self.actual_tools,

            "tool_selection_correct":
                self.tool_selection_correct,

            "verification_expected":
                self.verification_expected,

            "verification_success":
                self.verification_success,

            "recovery_expected":
                self.recovery_expected,

            "recovery_success":
                self.recovery_success,

            "execution_latency_ms":
                round(
                    self.execution_latency_ms,
                    2
                ),

            "started_at":
                self.started_at,

            "completed_at":
                self.completed_at,

            "error":
                self.error,

            "metadata":
                self.metadata,
        }


# =========================================================
# AGENT EVALUATION ENGINE
# =========================================================

class AgentEvaluationEngine:

    def __init__(self):

        self.records: list[
            EvaluationRecord
        ] = []

    # =====================================================
    # RESET
    # =====================================================

    def reset(self) -> None:

        self.records.clear()

    # =====================================================
    # RECORD BENCHMARK RESULT
    # =====================================================

    def record(
        self,
        benchmark_id: str,
        execution_result: dict[str, Any],
        expected_tools: Optional[
            list[str]
        ] = None,
        verification_expected: bool = False,
        recovery_expected: bool = False,
        latency_ms: Optional[float] = None,
    ) -> EvaluationRecord:

        expected_tools = (
            expected_tools or []
        )

        execution_result = (
            execution_result or {}
        )

        tasks = self._extract_tasks(
            execution_result
        )

        total_tasks = len(tasks)

        completed_tasks = sum(
            1
            for task in tasks
            if self._is_completed(task)
        )

        actual_tools = (
            self._extract_tools(
                execution_result
            )
        )

        success = (
            execution_result.get(
                "success",
                False
            )
            is True
        )

        if not success:

            success = (
                execution_result.get(
                    "status"
                )
                == "completed"
            )

        tool_selection_correct = (
            self._check_tool_selection(
                expected_tools,
                actual_tools
            )
        )

        verification_success = (
            self._check_verification(
                execution_result
            )
        )

        recovery_success = (
            self._check_recovery(
                execution_result
            )
        )

        if latency_ms is None:

            latency_ms = (
                self._calculate_latency(
                    execution_result
                )
            )

        started_at = (
            execution_result.get(
                "started_at"
            )
        )

        completed_at = (
            execution_result.get(
                "completed_at"
            )
        )

        record = EvaluationRecord(

            benchmark_id=
                benchmark_id,

            success=
                success,

            total_tasks=
                total_tasks,

            completed_tasks=
                completed_tasks,

            expected_tools=
                list(expected_tools),

            actual_tools=
                actual_tools,

            tool_selection_correct=
                tool_selection_correct,

            verification_expected=
                verification_expected,

            verification_success=
                verification_success,

            recovery_expected=
                recovery_expected,

            recovery_success=
                recovery_success,

            execution_latency_ms=
                latency_ms,

            started_at=
                started_at,

            completed_at=
                completed_at,

            error=
                execution_result.get(
                    "error"
                ),

            metadata={
                "status":
                    execution_result.get(
                        "status"
                    ),

                "execution_id":
                    execution_result.get(
                        "execution_id"
                    ),
            },
        )

        self.records.append(
            record
        )

        return record

    # =====================================================
    # EXTRACT TASKS
    # =====================================================

    def _extract_tasks(
        self,
        execution_result: dict[str, Any]
    ) -> list[dict[str, Any]]:

        plan = execution_result.get(
            "plan"
        )

        if isinstance(
            plan,
            list
        ):

            flattened = []

            for task in plan:

                if not isinstance(
                    task,
                    dict
                ):

                    continue

                subtasks = task.get(
                    "subtasks"
                )

                if isinstance(
                    subtasks,
                    list
                ) and subtasks:

                    for subtask in subtasks:

                        if isinstance(
                            subtask,
                            dict
                        ):

                            flattened.append(
                                subtask
                            )

                else:

                    flattened.append(
                        task
                    )

            return flattened

        tasks = execution_result.get(
            "tasks"
        )

        if isinstance(
            tasks,
            list
        ):

            return [
                task
                for task in tasks
                if isinstance(
                    task,
                    dict
                )
            ]

        return []

    # =====================================================
    # CHECK TASK COMPLETION
    # =====================================================

    def _is_completed(
        self,
        task: dict[str, Any]
    ) -> bool:

        return (
            task.get("status")
            == "completed"
        )

    # =====================================================
    # EXTRACT USED TOOLS
    # =====================================================

    def _extract_tools(
        self,
        execution_result: dict[str, Any]
    ) -> list[str]:

        tools = []

        trace = execution_result.get(
            "execution_trace"
        )

        if isinstance(
            trace,
            list
        ):

            for event in trace:

                if not isinstance(
                    event,
                    dict
                ):

                    continue

                data = event.get(
                    "data",
                    {}
                )

                if not isinstance(
                    data,
                    dict
                ):

                    continue

                tool = data.get(
                    "tool"
                )

                if tool and tool not in tools:

                    tools.append(
                        str(tool)
                    )

        # -------------------------------------------------
        # Also inspect task results
        # -------------------------------------------------

        tasks = self._extract_tasks(
            execution_result
        )

        for task in tasks:

            result = task.get(
                "result"
            )

            if isinstance(
                result,
                dict
            ):

                tool = result.get(
                    "tool"
                )

                if tool and tool not in tools:

                    tools.append(
                        str(tool)
                    )

            elif isinstance(
                result,
                str
            ):

                for known_tool in (
                    "calculator",
                    "web_research",
                    "browser",
                    "computer"
                ):

                    if known_tool in result:
                        if known_tool not in tools:
                            tools.append(
                                known_tool
                            )

        return tools

    # =====================================================
    # TOOL SELECTION ACCURACY
    # =====================================================

    def _check_tool_selection(
        self,
        expected_tools: list[str],
        actual_tools: list[str]
    ) -> bool:

        if not expected_tools:

            return True

        if not actual_tools:

            return False

        expected = {
            str(tool).lower()
            for tool in expected_tools
        }

        actual = {
            str(tool).lower()
            for tool in actual_tools
        }

        return expected.issubset(
            actual
        )

    # =====================================================
    # VERIFICATION
    # =====================================================

    def _check_verification(
        self,
        execution_result: dict[str, Any]
    ) -> bool:

        verification = (
            execution_result.get(
                "verification"
            )
        )

        if not isinstance(
            verification,
            list
        ):

            return False

        if not verification:

            return False

        successful = 0

        for item in verification:

            if not isinstance(
                item,
                dict
            ):

                continue

            if item.get(
                "success"
            ) is True:

                successful += 1

                continue

            if item.get(
                "verified"
            ) is True:

                successful += 1

                continue

            if item.get(
                "status"
            ) == "verified":

                successful += 1

        return successful > 0

    # =====================================================
    # RECOVERY
    # =====================================================

    def _check_recovery(
        self,
        execution_result: dict[str, Any]
    ) -> bool:

        recovery = (
            execution_result.get(
                "recovery"
            )
        )

        if isinstance(
            recovery,
            list
        ):

            for item in recovery:

                if not isinstance(
                    item,
                    dict
                ):

                    continue

                if item.get(
                    "recovered"
                ) is True:

                    return True

        replanning = (
            execution_result.get(
                "replanning"
            )
        )

        if isinstance(
            replanning,
            list
        ) and replanning:

            return True

        return False

    # =====================================================
    # LATENCY
    # =====================================================

    def _calculate_latency(
        self,
        execution_result: dict[str, Any]
    ) -> float:

        started = (
            execution_result.get(
                "started_at"
            )
        )

        completed = (
            execution_result.get(
                "completed_at"
            )
        )

        if not started or not completed:

            return 0.0

        try:

            start_time = (
                datetime.fromisoformat(
                    started.replace(
                        "Z",
                        "+00:00"
                    )
                )
            )

            end_time = (
                datetime.fromisoformat(
                    completed.replace(
                        "Z",
                        "+00:00"
                    )
                )
            )

            return max(
                0.0,
                (
                    end_time -
                    start_time
                ).total_seconds()
                * 1000
            )

        except Exception:

            return 0.0

    # =====================================================
    # TASK COMPLETION RATE
    # =====================================================

    def task_completion_rate(
        self
    ) -> float:

        total_tasks = sum(
            record.total_tasks
            for record in self.records
        )

        completed_tasks = sum(
            record.completed_tasks
            for record in self.records
        )

        if total_tasks == 0:

            return 0.0

        return round(
            (
                completed_tasks
                / total_tasks
            )
            * 100,
            2
        )

    # =====================================================
    # SUCCESS RATE
    # =====================================================

    def success_rate(
        self
    ) -> float:

        total = len(
            self.records
        )

        if total == 0:

            return 0.0

        successful = sum(
            1
            for record in self.records
            if record.success
        )

        return round(
            (
                successful
                / total
            )
            * 100,
            2
        )

    # =====================================================
    # TOOL SELECTION ACCURACY
    # =====================================================

    def tool_selection_accuracy(
        self
    ) -> float:

        applicable = [
            record
            for record in self.records
            if record.expected_tools
        ]

        if not applicable:

            return 0.0

        correct = sum(
            1
            for record in applicable
            if record.tool_selection_correct
        )

        return round(
            (
                correct
                / len(applicable)
            )
            * 100,
            2
        )

    # =====================================================
    # VERIFICATION ACCURACY
    # =====================================================

    def verification_accuracy(
        self
    ) -> float:

        applicable = [
            record
            for record in self.records
            if record.verification_expected
        ]

        if not applicable:

            return 0.0

        correct = sum(
            1
            for record in applicable
            if record.verification_success
        )

        return round(
            (
                correct
                / len(applicable)
            )
            * 100,
            2
        )

    # =====================================================
    # RECOVERY RATE
    # =====================================================

    def recovery_rate(
        self
    ) -> float:

        applicable = [
            record
            for record in self.records
            if record.recovery_expected
        ]

        if not applicable:

            return 0.0

        recovered = sum(
            1
            for record in applicable
            if record.recovery_success
        )

        return round(
            (
                recovered
                / len(applicable)
            )
            * 100,
            2
        )

    # =====================================================
    # AVERAGE LATENCY
    # =====================================================

    def average_latency_ms(
        self
    ) -> float:

        if not self.records:

            return 0.0

        total = sum(
            record.execution_latency_ms
            for record in self.records
        )

        return round(
            total / len(self.records),
            2
        )

    # =====================================================
    # FULL EVALUATION REPORT
    # =====================================================

    def generate_report(
        self
    ) -> dict[str, Any]:

        return {
            "total_benchmarks":
                len(self.records),

            "successful_benchmarks":
                sum(
                    1
                    for record in self.records
                    if record.success
                ),

            "failed_benchmarks":
                sum(
                    1
                    for record in self.records
                    if not record.success
                ),

            "success_rate":
                self.success_rate(),

            "task_completion_rate":
                self.task_completion_rate(),

            "tool_selection_accuracy":
                self.tool_selection_accuracy(),

            "verification_accuracy":
                self.verification_accuracy(),

            "recovery_rate":
                self.recovery_rate(),

            "average_execution_latency_ms":
                self.average_latency_ms(),

            "records": [
                record.to_dict()
                for record in self.records
            ],
        }

    # =====================================================
    # GET RECORDS
    # =====================================================

    def get_records(
        self
    ) -> list[dict[str, Any]]:

        return [
            record.to_dict()
            for record in self.records
        ]


# =========================================================
# GLOBAL EVALUATION ENGINE
# =========================================================

evaluation_engine = (
    AgentEvaluationEngine()
)  