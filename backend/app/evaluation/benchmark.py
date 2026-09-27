from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class BenchmarkCase:
    """
    Represents one evaluation benchmark for AURA.
    """

    id: str
    name: str
    goal: str

    expected_tools: list[str] = field(
        default_factory=list
    )

    expected_status: str = "completed"

    description: str = ""

    tags: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "expected_tools": self.expected_tools,
            "expected_status": self.expected_status,
            "description": self.description,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class BenchmarkSuite:
    """
    Stores and manages AURA evaluation benchmarks.
    """

    def __init__(
        self,
        benchmarks: Optional[
            list[BenchmarkCase]
        ] = None
    ):
        self._benchmarks = (
            benchmarks or []
        )

    # =====================================================
    # ADD BENCHMARK
    # =====================================================

    def add(
        self,
        benchmark: BenchmarkCase
    ) -> BenchmarkCase:

        if not isinstance(
            benchmark,
            BenchmarkCase
        ):
            raise TypeError(
                "benchmark must be a BenchmarkCase."
            )

        if self.get(
            benchmark.id
        ) is not None:

            raise ValueError(
                f"Benchmark '{benchmark.id}' already exists."
            )

        self._benchmarks.append(
            benchmark
        )

        return benchmark

    # =====================================================
    # GET BENCHMARK
    # =====================================================

    def get(
        self,
        benchmark_id: str
    ) -> Optional[BenchmarkCase]:

        for benchmark in self._benchmarks:

            if benchmark.id == benchmark_id:

                return benchmark

        return None

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(
        self
    ) -> list[BenchmarkCase]:

        return list(
            self._benchmarks
        )

    # =====================================================
    # COUNT
    # =====================================================

    def count(self) -> int:

        return len(
            self._benchmarks
        )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self) -> None:

        self._benchmarks.clear()

    # =====================================================
    # SERIALIZE
    # =====================================================

    def to_list(
        self
    ) -> list[dict[str, Any]]:

        return [
            benchmark.to_dict()
            for benchmark
            in self._benchmarks
        ]


# =========================================================
# DEFAULT AURA BENCHMARKS
# =========================================================

DEFAULT_BENCHMARKS = [

    BenchmarkCase(
        id="calculator_basic",
        name="Basic Calculation",
        goal=(
            "Calculate 2500 multiplied by 3"
        ),
        expected_tools=[
            "calculator"
        ],
        expected_status="completed",
        description=(
            "Tests whether AURA can identify "
            "a mathematical objective and "
            "select the calculator tool."
        ),
        tags=[
            "calculator",
            "basic",
            "tool_selection"
        ],
    ),

    BenchmarkCase(
        id="calculator_addition",
        name="Addition Calculation",
        goal=(
            "Calculate 500 plus 750"
        ),
        expected_tools=[
            "calculator"
        ],
        expected_status="completed",
        description=(
            "Tests basic arithmetic execution "
            "using the calculator tool."
        ),
        tags=[
            "calculator",
            "arithmetic"
        ],
    ),

    BenchmarkCase(
        id="web_research",
        name="Web Research",
        goal=(
            "Research the latest stable "
            "Python version"
        ),
        expected_tools=[
            "web_research"
        ],
        expected_status="completed",
        description=(
            "Tests whether AURA can recognize "
            "a research objective and select "
            "the web research tool."
        ),
        tags=[
            "research",
            "web",
            "tool_selection"
        ],
    ),

    BenchmarkCase(
        id="browser_open",
        name="Browser Navigation",
        goal=(
            "Open https://example.com and "
            "extract the page title"
        ),
        expected_tools=[
            "browser"
        ],
        expected_status="completed",
        description=(
            "Tests browser navigation and "
            "page information extraction."
        ),
        tags=[
            "browser",
            "navigation"
        ],
    ),

    BenchmarkCase(
        id="calculation_verification",
        name="Calculation Verification",
        goal=(
            "Calculate 500 plus 750 and "
            "verify the result"
        ),
        expected_tools=[
            "calculator"
        ],
        expected_status="completed",
        description=(
            "Tests calculation execution followed "
            "by result verification."
        ),
        tags=[
            "calculator",
            "verification"
        ],
    ),

    BenchmarkCase(
        id="research_summary",
        name="Research Summary",
        goal=(
            "Research Python programming and "
            "summarize the important findings"
        ),
        expected_tools=[
            "web_research"
        ],
        expected_status="completed",
        description=(
            "Tests research execution and "
            "final result generation."
        ),
        tags=[
            "research",
            "summary",
            "result_generation"
        ],
    ),
]


# =========================================================
# DEFAULT BENCHMARK SUITE
# =========================================================

benchmark_suite = BenchmarkSuite(
    benchmarks=list(
        DEFAULT_BENCHMARKS
    )
)