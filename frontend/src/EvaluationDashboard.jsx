import React, { useCallback, useEffect, useState } from "react";
import "./EvaluationDashboard.css";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "https://aura-autonomous-universal-reasoning-agent.onrender.com";

function formatPercentage(value) {
  const number = Number(value || 0);
  return `${number.toFixed(1)}%`;
}

function formatLatency(value) {
  const number = Number(value || 0);

  if (number < 1000) {
    return `${number.toFixed(0)} ms`;
  }

  return `${(number / 1000).toFixed(2)} s`;
}

function getBenchmarkName(benchmark) {
  return (
    benchmark?.name ||
    benchmark?.title ||
    benchmark?.id ||
    "Unnamed Benchmark"
  );
}

function getBenchmarkGoal(benchmark) {
  return benchmark?.goal || "No benchmark objective specified.";
}

function getBenchmarkTags(benchmark) {
  return Array.isArray(benchmark?.tags) ? benchmark.tags : [];
}

function getResultStatus(record) {
  if (record?.success) {
    return "success";
  }

  return "failed";
}

export default function EvaluationDashboard() {
  const [benchmarks, setBenchmarks] = useState([]);
  const [report, setReport] = useState(null);
  const [results, setResults] = useState([]);

  const [loading, setLoading] = useState(true);
  const [runningBenchmark, setRunningBenchmark] = useState(null);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [benchmarksResponse, reportResponse, resultsResponse] =
        await Promise.all([
          fetch(`${API_BASE}/evaluation/benchmarks`),
          fetch(`${API_BASE}/evaluation/report`),
          fetch(`${API_BASE}/evaluation/results`),
        ]);

      if (!benchmarksResponse.ok) {
        throw new Error(
          `Failed to load benchmarks (${benchmarksResponse.status})`
        );
      }

      if (!reportResponse.ok) {
        throw new Error(
          `Failed to load evaluation report (${reportResponse.status})`
        );
      }

      if (!resultsResponse.ok) {
        throw new Error(
          `Failed to load evaluation results (${resultsResponse.status})`
        );
      }

      const benchmarksData = await benchmarksResponse.json();
      const reportData = await reportResponse.json();
      const resultsData = await resultsResponse.json();

      setBenchmarks(
        Array.isArray(benchmarksData?.benchmarks)
          ? benchmarksData.benchmarks
          : []
      );

      setReport(reportData?.report || null);

      setResults(
        Array.isArray(resultsData?.results)
          ? resultsData.results
          : []
      );
    } catch (err) {
      setError(
        err?.message ||
          "Unable to load the evaluation dashboard."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const runBenchmark = async (benchmarkId) => {
    if (!benchmarkId) {
      return;
    }

    setRunningBenchmark(benchmarkId);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/evaluation/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          benchmark_id: benchmarkId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            `Benchmark execution failed (${response.status})`
        );
      }

      await loadDashboard();
    } catch (err) {
      setError(
        err?.message ||
          "Benchmark execution failed."
      );
    } finally {
      setRunningBenchmark(null);
    }
  };

  const clearResults = async () => {
    if (results.length === 0) {
      return;
    }

    setError("");

    try {
      const response = await fetch(`${API_BASE}/evaluation/results`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            `Unable to clear evaluation results (${response.status})`
        );
      }

      await loadDashboard();
    } catch (err) {
      setError(
        err?.message ||
          "Unable to clear evaluation results."
      );
    }
  };

  const totalBenchmarks = Number(
    report?.total_benchmarks || 0
  );

  const successfulBenchmarks = Number(
  report?.successful_benchmarks || 0
    );

  const successRate = Number(
    report?.success_rate || 0
  );

  const toolAccuracy = Number(
    report?.tool_selection_accuracy || 0
  );

  const verificationAccuracy = Number(
    report?.verification_accuracy || 0
  );

  const recoveryRate = Number(
    report?.recovery_rate || 0
  );

  const averageLatency = Number(
    report?.average_latency_ms || 0
  );

  return (
    <div className="evaluation-page">
      {/* Header */}

      <div className="evaluation-header">
        <div className="evaluation-header-top">
          <div>
            <h1 className="evaluation-title">
              Agent Evaluation
            </h1>

            <p className="evaluation-subtitle">
              Benchmark and measure AURA's autonomous capabilities
            </p>
          </div>

          <div className="evaluation-actions">
            <button
              type="button"
              className="evaluation-btn"
              onClick={loadDashboard}
              disabled={loading}
            >
              {loading ? "Refreshing..." : "↻ Refresh"}
            </button>

            <button
              type="button"
              className="evaluation-btn"
              onClick={clearResults}
              disabled={results.length === 0}
            >
              Clear Results
            </button>
          </div>
        </div>
      </div>

      {/* Error */}

      {error && (
        <div className="evaluation-error">
          {error}
        </div>
      )}

      {/* Warning */}

      <div className="evaluation-warning">
        <div className="evaluation-warning-icon">
          ⚠
        </div>

        <div className="evaluation-warning-content">
          <p className="evaluation-warning-title">
            Benchmark execution uses the AURA execution pipeline
          </p>

          <p className="evaluation-warning-text">
            Running a benchmark may use the configured LLM
            planner and external research tools. Use individual
            benchmark execution when you actually want to measure
            the agent.
          </p>
        </div>
      </div>

      {/* Metrics */}

      <section className="evaluation-section">
        <div className="evaluation-section-header">
          <div>
            <h2 className="evaluation-section-title">
              Evaluation Metrics
            </h2>

            <p className="evaluation-section-description">
              Current performance across recorded evaluations
            </p>
          </div>
        </div>

        {loading && !report ? (
          <div className="evaluation-loading">
            <span className="evaluation-spinner" />
            Loading evaluation metrics...
          </div>
        ) : (
          <div className="evaluation-metrics">
            <div className="evaluation-metric-card">
              <p className="evaluation-metric-label">
                Success Rate
              </p>

              <p className="evaluation-metric-value">
                {formatPercentage(successRate)}
              </p>

              <p className="evaluation-metric-description">
                {successfulBenchmarks} successful /{" "}
                {totalBenchmarks} evaluated
              </p>
            </div>

            <div className="evaluation-metric-card">
              <p className="evaluation-metric-label">
                Tool Accuracy
              </p>

              <p className="evaluation-metric-value">
                {formatPercentage(toolAccuracy)}
              </p>

              <p className="evaluation-metric-description">
                Correct tool selection
              </p>
            </div>

            <div className="evaluation-metric-card">
              <p className="evaluation-metric-label">
                Verification
              </p>

              <p className="evaluation-metric-value">
                {formatPercentage(verificationAccuracy)}
              </p>

              <p className="evaluation-metric-description">
                Verification success
              </p>
            </div>

            <div className="evaluation-metric-card">
              <p className="evaluation-metric-label">
                Recovery
              </p>

              <p className="evaluation-metric-value">
                {formatPercentage(recoveryRate)}
              </p>

              <p className="evaluation-metric-description">
                Failure recovery success
              </p>
            </div>

            <div className="evaluation-metric-card">
              <p className="evaluation-metric-label">
                Avg. Latency
              </p>

              <p className="evaluation-metric-value">
                {formatLatency(averageLatency)}
              </p>

              <p className="evaluation-metric-description">
                Average execution time
              </p>
            </div>
          </div>
        )}
      </section>

      {/* Benchmarks */}

      <section className="evaluation-section">
        <div className="evaluation-section-header">
          <div>
            <h2 className="evaluation-section-title">
              Benchmark Suite
            </h2>

            <p className="evaluation-section-description">
              {benchmarks.length} benchmark
              {benchmarks.length === 1 ? "" : "s"} configured
            </p>
          </div>
        </div>

        {loading && benchmarks.length === 0 ? (
          <div className="evaluation-loading">
            <span className="evaluation-spinner" />
            Loading benchmarks...
          </div>
        ) : benchmarks.length === 0 ? (
          <div className="evaluation-results-card">
            <div className="evaluation-empty">
              No benchmarks are currently configured.
            </div>
          </div>
        ) : (
          <div className="evaluation-benchmarks">
            {benchmarks.map((benchmark) => {
              const benchmarkId = benchmark?.id;
              const tags = getBenchmarkTags(benchmark);
              const isRunning =
                runningBenchmark === benchmarkId;

              return (
                <div
                  className="evaluation-benchmark-card"
                  key={benchmarkId}
                >
                  <div className="evaluation-benchmark-top">
                    <div>
                      <h3 className="evaluation-benchmark-name">
                        {getBenchmarkName(benchmark)}
                      </h3>

                      <p className="evaluation-benchmark-id">
                        {benchmarkId}
                      </p>
                    </div>

                    <button
                      type="button"
                      className="evaluation-run-btn"
                      onClick={() =>
                        runBenchmark(benchmarkId)
                      }
                      disabled={
                        Boolean(runningBenchmark) ||
                        !benchmarkId
                      }
                    >
                      {isRunning
                        ? "Running..."
                        : "Run Test"}
                    </button>
                  </div>

                  <div className="evaluation-benchmark-goal">
                    {getBenchmarkGoal(benchmark)}
                  </div>

                  <div className="evaluation-tags">
                    {tags.length > 0 ? (
                      tags.map((tag) => (
                        <span
                          className="evaluation-tag"
                          key={`${benchmarkId}-${tag}`}
                        >
                          {tag}
                        </span>
                      ))
                    ) : (
                      <span className="evaluation-tag">
                        standard
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Results */}

      <section className="evaluation-section">
        <div className="evaluation-section-header">
          <div>
            <h2 className="evaluation-section-title">
              Recent Evaluation Results
            </h2>

            <p className="evaluation-section-description">
              Recorded benchmark execution results
            </p>
          </div>
        </div>

        <div className="evaluation-results-card">
          {results.length === 0 ? (
            <div className="evaluation-empty">
              No evaluation results yet.
              <br />
              Run a benchmark when you are ready to measure AURA.
            </div>
          ) : (
            <div className="evaluation-table-wrapper">
              <table className="evaluation-table">
                <thead>
                  <tr>
                    <th>Benchmark</th>
                    <th>Status</th>
                    <th>Tasks</th>
                    <th>Tool Selection</th>
                    <th>Latency</th>
                  </tr>
                </thead>

                <tbody>
                  {results
                    .slice()
                    .reverse()
                    .map((record, index) => {
                      const status =
                        getResultStatus(record);

                      const completedTasks = Number(
                        record?.completed_tasks || 0
                      );

                      const totalTasks = Number(
                        record?.total_tasks || 0
                      );

                      const toolSelectionCorrect =
                        record?.tool_selection_correct;

                      const latency =
                        Number(
                          record?.execution_latency_ms || 0
                        );

                      return (
                        <tr
                          key={
                            `${record?.benchmark_id || "result"}-${index}`
                          }
                        >
                          <td>
                            {record?.benchmark_id ||
                              "Unknown"}
                          </td>

                          <td>
                            <span
                              className={`evaluation-status ${
                                status === "success"
                                  ? "evaluation-status-success"
                                  : "evaluation-status-failed"
                              }`}
                            >
                              {status === "success"
                                ? "✓ Passed"
                                : "✕ Failed"}
                            </span>
                          </td>

                          <td>
                            {completedTasks} / {totalTasks}
                          </td>

                          <td>
                            {toolSelectionCorrect
                              ? "✓ Correct"
                              : "—"}
                          </td>

                          <td>
                            {formatLatency(latency)}
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}