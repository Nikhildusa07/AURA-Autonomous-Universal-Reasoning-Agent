from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.evaluation.benchmark import benchmark_suite
from backend.app.evaluation.evaluator import evaluation_engine
from backend.app.api.agent import AgentRequest, run_agent


router = APIRouter(
    prefix="/evaluation",
    tags=["Evaluation"],
)


# =========================================================
# REQUEST MODELS
# =========================================================

class RecordEvaluationRequest(BaseModel):
    benchmark_id: str
    execution_result: dict[str, Any]
    latency_ms: float | None = Field(
        default=None,
        ge=0,
    )


class RunBenchmarkRequest(BaseModel):
    benchmark_id: str


# =========================================================
# BENCHMARKS
# =========================================================

@router.get("/benchmarks")
def get_benchmarks():
    return {
        "success": True,
        "count": benchmark_suite.count(),
        "benchmarks": benchmark_suite.to_list(),
    }


@router.get("/benchmarks/{benchmark_id}")
def get_benchmark(benchmark_id: str):
    benchmark = benchmark_suite.get(benchmark_id)

    if benchmark is None:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark '{benchmark_id}' not found.",
        )

    return {
        "success": True,
        "benchmark": benchmark.to_dict(),
    }


# =========================================================
# RECORD EXISTING EXECUTION
# =========================================================

@router.post("/record")
def record_evaluation(
    request: RecordEvaluationRequest,
):
    benchmark = benchmark_suite.get(
        request.benchmark_id
    )

    if benchmark is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Benchmark "
                f"'{request.benchmark_id}' not found."
            ),
        )

    verification_expected = (
        "verification" in benchmark.tags
    )

    recovery_expected = (
        "recovery" in benchmark.tags
    )

    record = evaluation_engine.record(
        benchmark_id=benchmark.id,
        execution_result=request.execution_result,
        expected_tools=benchmark.expected_tools,
        verification_expected=verification_expected,
        recovery_expected=recovery_expected,
        latency_ms=request.latency_ms,
    )

    return {
        "success": True,
        "benchmark": benchmark.to_dict(),
        "evaluation": record.to_dict(),
        "report": evaluation_engine.generate_report(),
    }


# =========================================================
# RUN ONE BENCHMARK
# =========================================================

@router.post("/run")
def run_benchmark(
    request: RunBenchmarkRequest,
):
    benchmark = benchmark_suite.get(
        request.benchmark_id
    )

    if benchmark is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Benchmark "
                f"'{request.benchmark_id}' not found."
            ),
        )

    started = time.perf_counter()

    try:
        execution_result = run_agent(
            AgentRequest(
                goal=benchmark.goal
            )
        )

        latency_ms = (
            time.perf_counter() - started
        ) * 1000

        record = evaluation_engine.record(
            benchmark_id=benchmark.id,
            execution_result=execution_result,
            expected_tools=benchmark.expected_tools,
            verification_expected=(
                "verification" in benchmark.tags
            ),
            recovery_expected=(
                "recovery" in benchmark.tags
            ),
            latency_ms=latency_ms,
        )

        return {
            "success": True,
            "benchmark": benchmark.to_dict(),
            "execution": execution_result,
            "evaluation": record.to_dict(),
            "report": evaluation_engine.generate_report(),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# REPORT
# =========================================================

@router.get("/report")
def get_evaluation_report():
    return {
        "success": True,
        "report": evaluation_engine.generate_report(),
    }


# =========================================================
# RESULTS
# =========================================================

@router.get("/results")
def get_evaluation_results():
    return {
        "success": True,
        "results": evaluation_engine.get_records(),
    }


# =========================================================
# RESET
# =========================================================

@router.delete("/results")
def clear_evaluation_results():
    evaluation_engine.reset()

    return {
        "success": True,
        "message": "Evaluation results cleared.",
    }