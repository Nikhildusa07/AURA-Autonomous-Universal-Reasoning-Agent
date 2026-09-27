import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import EvaluationDashboard from "./EvaluationDashboard";

import {
  runAgent,
  getExecutions,
  getExecution,
  getPendingInterventions,
  approveIntervention,
  rejectIntervention,
  resumeIntervention,
} from "./api";


/* =========================================================
   SAFE DISPLAY HELPERS
========================================================= */

function safeText(value, fallback = "") {
  if (
    value === null ||
    value === undefined
  ) {
    return fallback;
  }

  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value
      .map((item) => safeText(item))
      .filter(Boolean)
      .join(", ");
  }

  if (typeof value === "object") {
    try {
      if (
        value.answer !== undefined
      ) {
        return safeText(
          value.answer,
          fallback
        );
      }

      if (
        value.result !== undefined &&
        (
          typeof value.result ===
            "string" ||
          typeof value.result ===
            "number"
        )
      ) {
        return safeText(
          value.result,
          fallback
        );
      }

      if (
        value.message !== undefined
      ) {
        return safeText(
          value.message,
          fallback
        );
      }

      return JSON.stringify(
        value,
        null,
        2
      );
    } catch {
      return fallback;
    }
  }

  return String(value);
}


function safeRender(value, fallback = "—") {
  const text = safeText(
    value,
    fallback
  );

  return text || fallback;
}


function safeObject(value) {
  if (
    value &&
    typeof value === "object" &&
    !Array.isArray(value)
  ) {
    return value;
  }

  return {};
}


function safeArray(value) {
  return Array.isArray(value)
    ? value
    : [];
}


/* =========================================================
   FINAL RESULT DISPLAY HELPER
========================================================= */

function getFinalAnswer(finalResult) {
  if (!finalResult) {
    return "";
  }

  if (
    typeof finalResult === "string" ||
    typeof finalResult === "number"
  ) {
    return String(finalResult);
  }

  if (
    typeof finalResult !== "object"
  ) {
    return String(finalResult);
  }

  if (
    finalResult.answer !==
      undefined &&
    finalResult.answer !== null
  ) {
    return safeText(
      finalResult.answer
    );
  }

  if (
    finalResult.summary !==
      undefined &&
    finalResult.summary !== null
  ) {
    return safeText(
      finalResult.summary
    );
  }

  if (
    finalResult.message !==
      undefined &&
    finalResult.message !== null
  ) {
    return safeText(
      finalResult.message
    );
  }

  if (
    finalResult.result !==
      undefined &&
    finalResult.result !== null
  ) {
    return safeText(
      finalResult.result
    );
  }

  return safeText(
    finalResult,
    "AURA completed the execution pipeline."
  );
}


/* =========================================================
   KEY RESULT FORMATTER
========================================================= */

function formatKeyResult(item) {
  if (!item) {
    return "";
  }

  if (
    typeof item !== "object"
  ) {
    return safeText(item);
  }

  if (
    item.type === "calculation"
  ) {
    const expression =
      safeText(
        item.expression,
        "Calculation"
      );

    const calculationResult =
      safeText(
        item.result,
        "—"
      );

    return `${expression} = ${calculationResult}`;
  }

  if (
    item.type === "research"
  ) {
    return `Research query: ${safeText(
      item.query,
      "Unknown"
    )} • ${safeText(
      item.result_count,
      "0"
    )} sources`;
  }

  if (
    item.type === "browser" ||
    item.type === "computer"
  ) {
    return safeText(
      item.title ||
        item.url ||
        item.text,
      "Browser interaction completed"
    );
  }

  return safeText(
    item,
    "Result available"
  );
}


/* =========================================================
   APP
========================================================= */

function App() {
  const [goal, setGoal] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [result, setResult] =
    useState(null);

  const [error, setError] =
    useState("");

  const [activeView, setActiveView] =
    useState("command");

  return (
    <div className="aura-app">
      <div className="background-grid" />
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <span />
            <span />
            <span />
          </div>

          <div>
            <div className="brand-name">
              AURA
            </div>

            <div className="brand-subtitle">
              Autonomous Intelligence
            </div>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-label">
            WORKSPACE
          </div>

          <button
            className={`nav-item ${
              activeView === "command"
                ? "nav-active"
                : ""
            }`}
            onClick={() =>
              setActiveView("command")
            }
          >
            <span className="nav-icon">
              ⌂
            </span>

            <span>
              Command Center
            </span>
          </button>

          <button
            className={`nav-item ${
              activeView === "executions"
                ? "nav-active"
                : ""
            }`}
            onClick={() =>
              setActiveView("executions")
            }
          >
            <span className="nav-icon">
              ◇
            </span>

            <span>
              Executions
            </span>
          </button>

          <button
            className={`nav-item ${
              activeView === "memory"
                ? "nav-active"
                : ""
            }`}
            onClick={() =>
              setActiveView("memory")
            }
          >
            <span className="nav-icon">
              ◎
            </span>

            <span>
              Memory
            </span>
          </button>

          <button
            className={`nav-item ${
              activeView === "intervention"
                ? "nav-active"
                : ""
            }`}
            onClick={() =>
              setActiveView("intervention")
            }
          >
            <span className="nav-icon">
              ϟ
            </span>

            <span>
              Intervention
            </span>
          </button>

          <button
            className={`nav-item ${
              activeView === "evaluation"
                ? "nav-active"
                : ""
            }`}
            onClick={() =>
              setActiveView("evaluation")
            }
          >
            <span className="nav-icon">
              ?
            </span>

            <span>
              Evaluation
            </span>
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-label">
            AGENT
          </div>

          <div className="agent-status-card">
            <div className="agent-orb orb-active">
              <div className="orb-core" />
            </div>

            <div>
              <div className="agent-status-title">
                AURA Core
              </div>

              <div className="agent-status-line">
                <span className="online-dot" />
                System online
              </div>
            </div>
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="system-card">
            <div className="system-card-header">
              <span>
                CORE STATUS
              </span>

              <span className="system-online">
                ONLINE
              </span>
            </div>

            <div className="system-bar">
              <span />
            </div>

            <div className="system-details">
              <span>
                Planner
              </span>

              <strong>
                Ready
              </strong>
            </div>

            <div className="system-details">
              <span>
                Tools
              </span>

              <strong>
                3 active
              </strong>
            </div>

            <div className="system-details">
              <span>
                Memory
              </span>

              <strong>
                Persistent
              </strong>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="eyebrow">
              AUTONOMOUS AI PLATFORM
            </div>

            <h1>
              Command{" "}
              <span>
                Center
              </span>
            </h1>
          </div>

          <div className="topbar-right">
            <div className="global-status">
              <span
                className={`status-dot ${
                  loading
                    ? "status-running"
                    : ""
                }`}
              />

              {loading
                ? "Executing"
                : "Ready"}
            </div>

            <div className="avatar">
              A
            </div>
          </div>
        </header>

        {activeView === "command" && (
          <CommandCenter
            goal={goal}
            setGoal={setGoal}
            loading={loading}
            setLoading={setLoading}
            result={result}
            setResult={setResult}
            error={error}
            setError={setError}
          />
        )}

        {activeView === "executions" && (
          <ExecutionsView
            latestResult={result}
            onOpenExecution={(
              execution
            ) => {
              setResult(
                normalizeExecutionResult(
                  execution
                )
              );
              setActiveView(
                "command"
              );
            }}
          />
        )}

        {activeView === "memory" && (
          <MemoryView />
        )}

        {activeView ===
          "intervention" && (
          <InterventionPanel
            result={result}
            setResult={setResult}
          />
        )}

        {activeView === "evaluation" && (
          <EvaluationDashboard />
        )}

        <footer className="footer">
          <span>
            AURA • Autonomous Universal
            Reasoning Agent
          </span>

          <span>
            Local Runtime • v1.0.0
          </span>
        </footer>
      </main>
    </div>
  );
}


/* =========================================================
   COMMAND CENTER
========================================================= */

function CommandCenter({
  goal,
  setGoal,
  loading,
  setLoading,
  result,
  setResult,
  error,
  setError,
}) {
  const tasks = useMemo(() => {
    const plan =
      safeArray(
        result?.plan
      );

    const flattened = [];

    plan.forEach(
      (task) => {
        const subtasks =
          safeArray(
            task?.subtasks
          );

        if (
          subtasks.length > 0
        ) {
          subtasks.forEach(
            (subtask) => {
              flattened.push(
                safeObject(
                  subtask
                )
              );
            }
          );
        } else {
          flattened.push(
            safeObject(task)
          );
        }
      }
    );

    return flattened;
  }, [result]);

  const completedCount =
    tasks.filter(
      (task) =>
        task.status ===
        "completed"
    ).length;

  const failedCount =
    tasks.filter(
      (task) =>
        task.status === "failed"
    ).length;

  const pendingCount =
    tasks.filter(
      (task) =>
        task.status ===
          "pending" ||
        task.status ===
          "in_progress"
    ).length;

  const progress =
    tasks.length > 0
      ? Math.round(
          (completedCount /
            tasks.length) *
            100
        )
      : 0;

  const executionStatus =
    safeText(
      result?.status,
      "idle"
    );

  async function handleRun() {
    const trimmedGoal =
      goal.trim();

    if (!trimmedGoal) {
      setError(
        "Enter an objective for AURA."
      );

      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data =
        await runAgent(
          trimmedGoal
        );

      /*
       * Normalize the API response
       * immediately so React never
       * receives unsafe values.
       */
      setResult(
        normalizeExecutionResult(
          data
        )
      );
    } catch (requestError) {
      setError(
        safeText(
          requestError?.message,
          "Unable to connect to the AURA backend."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setGoal("");
    setResult(null);
    setError("");
  }

  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      (event.ctrlKey ||
        event.metaKey)
    ) {
      event.preventDefault();
      handleRun();
    }
  }

  function getTaskStatusClass(
    status
  ) {
    if (
      status === "completed"
    ) {
      return "task-status task-status-complete";
    }

    if (
      status === "failed"
    ) {
      return "task-status task-status-failed";
    }

    return "task-status task-status-pending";
  }

  function getStatusText(
    status
  ) {
    if (
      status === "completed"
    ) {
      return "Completed";
    }

    if (
      status === "failed"
    ) {
      return "Failed";
    }

    if (
      status === "pending"
    ) {
      return "Pending";
    }

    if (
      status === "in_progress"
    ) {
      return "Running";
    }

    return "Waiting";
  }

  function getExecutionStatusClass() {
    if (loading) {
      return "status-running";
    }

    if (
      executionStatus ===
      "completed"
    ) {
      return "status-success";
    }

    if (
      executionStatus ===
      "waiting_for_human"
    ) {
      return "status-warning";
    }

    if (
      executionStatus ===
      "failed"
    ) {
      return "status-error";
    }

    return "status-idle";
  }

  function getStatusLabel() {
    if (loading) {
      return "Executing";
    }

    if (
      executionStatus ===
      "completed"
    ) {
      return "Completed";
    }

    if (
      executionStatus ===
      "waiting_for_human"
    ) {
      return "Human Action";
    }

    if (
      executionStatus ===
      "failed"
    ) {
      return "Failed";
    }

    return "Ready";
  }

  const finalResult =
    safeObject(
      result?.final_result
    );

  const finalAnswer =
    getFinalAnswer(
      result?.final_result
    );

  const keyResults =
    safeArray(
      finalResult?.key_results
    );

  return (
    <>
      <section className="hero-grid">
        <div className="hero-copy">
          <div className="hero-badge">
            <span className="pulse-dot" />
            AUTONOMOUS MODE
          </div>

          <h2>
            Give AURA a goal.
            <br />

            <span>
              Let intelligence execute
              it.
            </span>
          </h2>

          <p>
            AURA understands complex
            objectives, decomposes them
            into tasks, selects tools,
            executes actions, evaluates
            results, and verifies the
            outcome.
          </p>
        </div>

        <div className="hero-orb-container">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />

          <div
            className={`large-orb ${
              loading
                ? "large-orb-active"
                : ""
            }`}
          >
            <div className="large-orb-inner">
              <span>
                A
              </span>
            </div>
          </div>

          <div className="orb-label">
            AURA CORE
          </div>
        </div>
      </section>

      <section className="command-card">
        <div className="command-header">
          <div>
            <div className="section-kicker">
              OBJECTIVE
            </div>

            <h3>
              What should AURA
              accomplish?
            </h3>
          </div>

          {goal && (
            <button
              className="clear-button"
              onClick={
                handleClear
              }
            >
              Clear
            </button>
          )}
        </div>

        <div className="input-shell">
          <div className="input-icon">
            ✦
          </div>

          <textarea
            value={goal}
            onChange={(event) =>
              setGoal(
                event.target.value
              )
            }
            onKeyDown={
              handleKeyDown
            }
            placeholder="Describe anything you want AURA to accomplish..."
            disabled={loading}
          />
        </div>

        <div className="command-footer">
          <div className="input-hint">
            <span>
              ⌘
            </span>

            AURA will plan, execute
            and verify the objective
            automatically.
          </div>

          <button
            className="execute-button"
            onClick={
              handleRun
            }
            disabled={loading}
          >
            {loading
              ? "Executing..."
              : "Run AURA"}

            <span className="button-arrow">
              {loading
                ? "…"
                : "→"}
            </span>
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <span>
              !
            </span>

            {safeRender(error)}
          </div>
        )}
      </section>

      <section className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon blue">
            ◇
          </div>

          <div>
            <div className="metric-value">
              {tasks.length}
            </div>

            <div className="metric-label">
              TASKS
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon green">
            ✓
          </div>

          <div>
            <div className="metric-value">
              {completedCount}
            </div>

            <div className="metric-label">
              COMPLETED
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon purple">
            %
          </div>

          <div>
            <div className="metric-value">
              {progress}%
            </div>

            <div className="metric-label">
              PROGRESS
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon orange">
            !
          </div>

          <div>
            <div className="metric-value">
              {failedCount +
                pendingCount}
            </div>

            <div className="metric-label">
              ATTENTION
            </div>
          </div>
        </div>
      </section>

      {result && (
        <section className="execution-layout">
          <div className="execution-main">
            <div className="panel-header">
              <div>
                <div className="section-kicker">
                  EXECUTION
                </div>

                <h3>
                  Agent Execution
                </h3>
              </div>

              <div
                className={`execution-badge ${getExecutionStatusClass()}`}
              >
                <span className="status-dot" />

                {getStatusLabel()}
              </div>
            </div>

            <div className="progress-container">
              <div className="progress-label">
                <span>
                  Objective progress
                </span>

                <strong>
                  {progress}%
                </strong>
              </div>

              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{
                    width: `${progress}%`,
                  }}
                />
              </div>
            </div>

            <div className="task-list">
              {tasks.length ===
              0 ? (
                <div className="task-row">
                  <div className="task-content">
                    <div className="task-title">
                      No individual
                      tasks returned.
                    </div>
                  </div>
                </div>
              ) : (
                tasks.map(
                  (
                    task,
                    index
                  ) => (
                    <div
                      className="task-row"
                      key={`${safeText(
                        task.id,
                        index
                      )}-${index}`}
                    >
                      <div
                        className={`task-number ${
                          task.status ===
                          "completed"
                            ? "task-complete"
                            : ""
                        }`}
                      >
                        {task.status ===
                        "completed"
                          ? "✓"
                          : index + 1}
                      </div>

                      <div className="task-content">
                        <div className="task-title">
                          {safeRender(
                            task.description,
                            "Unnamed task"
                          )}
                        </div>

                        <div className="task-meta">
                          Task ID:{" "}
                          {safeRender(
                            task.id
                          )}

                          {task.priority !==
                            undefined &&
                            task.priority !==
                              null && (
                              <>
                                {" • Priority: "}
                                {safeRender(
                                  task.priority
                                )}
                              </>
                            )}
                        </div>
                      </div>

                      <div
                        className={getTaskStatusClass(
                          task.status
                        )}
                      >
                        {getStatusText(
                          task.status
                        )}
                      </div>
                    </div>
                  )
                )
              )}
            </div>
          </div>

          <div className="execution-side">
            <div className="result-card">
              <div className="section-kicker">
                RESULT
              </div>

              <h3>
                Objective Outcome
              </h3>

              <div className="result-status">
                <div className="result-check">
                  {result.success
                    ? "✓"
                    : executionStatus ===
                      "waiting_for_human"
                    ? "!"
                    : "×"}
                </div>

                <div>
                  <strong>
                    {result.success
                      ? "Execution successful"
                      : executionStatus ===
                        "waiting_for_human"
                      ? "Human action required"
                      : "Execution incomplete"}
                  </strong>

                  <span>
                    {safeRender(
                      result.status
                    )}
                  </span>
                </div>
              </div>

              <div className="result-summary">
                <div
                  style={{
                    fontSize:
                      "16px",
                    lineHeight:
                      "1.7",
                    fontWeight:
                      600,
                    whiteSpace:
                      "pre-wrap",
                  }}
                >
                  {finalAnswer ||
                    "AURA completed the execution pipeline."}
                </div>
              </div>

              {keyResults.length >
                0 && (
                <div
                  className="result-summary"
                  style={{
                    marginTop:
                      "16px",
                  }}
                >
                  <div className="section-kicker">
                    KEY RESULTS
                  </div>

                  {keyResults.map(
                    (
                      item,
                      index
                    ) => (
                      <div
                        key={
                          index
                        }
                        style={{
                          marginTop:
                            "10px",
                        }}
                      >
                        {formatKeyResult(
                          item
                        )}
                      </div>
                    )
                  )}
                </div>
              )}
            </div>

            <div className="execution-info">
              <div className="section-kicker">
                EXECUTION INFO
              </div>

              <div className="info-row">
                <span>
                  Execution ID
                </span>

                <strong>
                  {result.execution_id
                    ? safeText(
                        result.execution_id
                      ).slice(
                        0,
                        8
                      )
                    : "—"}
                </strong>
              </div>

              <div className="info-row">
                <span>
                  Verification
                </span>

                <strong>
                  {safeArray(
                    result.verification
                  ).length
                    ? "Completed"
                    : "Pending"}
                </strong>
              </div>

              <div className="info-row">
                <span>
                  Memory
                </span>

                <strong>
                  {result.memory
                    ?.semantic_memory_updated
                    ? "Updated"
                    : "Stored"}
                </strong>
              </div>

              <div className="info-row">
                <span>
                  Persistence
                </span>

                <strong>
                  {result.execution_state
                    ?.persisted
                    ? "Saved"
                    : "Pending"}
                </strong>
              </div>
            </div>
          </div>
        </section>
      )}
    </>
  );
}


/* =========================================================
   EXECUTIONS VIEW
========================================================= */

function ExecutionsView({
  latestResult,
  onOpenExecution,
}) {
  const [executions, setExecutions] =
    useState([]);

  const [
    selectedExecution,
    setSelectedExecution,
  ] = useState(null);

  const [loading, setLoading] =
    useState(true);

  const [
    detailsLoading,
    setDetailsLoading,
  ] = useState(false);

  const [error, setError] =
    useState("");

  async function loadExecutions() {
    setLoading(true);
    setError("");

    try {
      const data =
        await getExecutions();

      const items =
        Array.isArray(
          data?.executions
        )
          ? data.executions
          : Array.isArray(data)
          ? data
          : [];

      setExecutions(
        items.map(
          (item) =>
            safeObject(item)
        )
      );
    } catch (
      requestError
    ) {
      setError(
        safeText(
          requestError?.message,
          "Unable to load execution history."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  async function openExecution(
    execution
  ) {
    const executionId =
      execution?.execution_id;

    if (!executionId) {
      setSelectedExecution(
        safeObject(execution)
      );
      return;
    }

    setDetailsLoading(true);
    setError("");

    try {
      const data =
        await getExecution(
          executionId
        );

      const details =
        data?.execution ||
        data?.data ||
        data;

      setSelectedExecution(
        safeObject(details)
      );
    } catch {
      setSelectedExecution(
        safeObject(execution)
      );
    } finally {
      setDetailsLoading(false);
    }
  }

  useEffect(() => {
    loadExecutions();
  }, []);

  function getHistoryStatusClass(
    status
  ) {
    if (
      status === "completed"
    ) {
      return "status-success";
    }

    if (
      status ===
      "waiting_for_human"
    ) {
      return "status-warning";
    }

    if (
      status === "failed"
    ) {
      return "status-error";
    }

    return "status-idle";
  }

  function formatGoal(goal) {
    return safeRender(
      goal,
      "Untitled execution"
    );
  }

  function formatDate(value) {
    if (!value) {
      return "Unknown time";
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return safeText(value);
    }

    return date.toLocaleString();
  }

  function countTasks(
    execution
  ) {
    if (
      Array.isArray(
        execution?.tasks
      )
    ) {
      return execution.tasks.length;
    }

    if (
      Array.isArray(
        execution?.plan
      )
    ) {
      let count = 0;

      execution.plan.forEach(
        (task) => {
          const subtasks =
            safeArray(
              task?.subtasks
            );

          if (
            subtasks.length
          ) {
            count +=
              subtasks.length;
          } else {
            count += 1;
          }
        }
      );

      return count;
    }

    return 0;
  }

  return (
    <section>
      <div className="command-card">
        <div className="command-header">
          <div>
            <div className="section-kicker">
              EXECUTIONS
            </div>

            <h3>
              Execution history
            </h3>
          </div>

          <button
            className="clear-button"
            onClick={
              loadExecutions
            }
            disabled={loading}
          >
            {loading
              ? "Loading..."
              : "Refresh"}
          </button>
        </div>

        {latestResult?.execution_id && (
          <div
            className="result-summary"
            style={{
              marginBottom:
                "18px",
            }}
          >
            Latest execution:{" "}
            <strong>
              {safeText(
                latestResult.execution_id
              )}
            </strong>
          </div>
        )}

        {error && (
          <div className="error-banner">
            <span>
              !
            </span>

            {safeRender(error)}
          </div>
        )}

        {loading ? (
          <div className="result-summary">
            Loading execution
            history...
          </div>
        ) : executions.length ===
          0 ? (
          <div className="result-summary">
            No saved executions
            found.
          </div>
        ) : (
          <div className="execution-history">
            {executions.map(
              (
                execution,
                index
              ) => (
                <button
                  type="button"
                  className="history-item"
                  key={
                    safeText(
                      execution.execution_id ||
                        execution.id,
                      index
                    )
                  }
                  onClick={() =>
                    openExecution(
                      execution
                    )
                  }
                >
                  <div className="history-index">
                    {index + 1}
                  </div>

                  <div className="history-content">
                    <div className="history-goal">
                      {formatGoal(
                        execution.goal
                      )}
                    </div>

                    <div className="history-meta">
                      <span>
                        ID:{" "}
                        {execution.execution_id
                          ? safeText(
                              execution.execution_id
                            ).slice(
                              0,
                              12
                            )
                          : safeRender(
                              execution.id
                            )}
                      </span>

                      <span>
                        Tasks:{" "}
                        {countTasks(
                          execution
                        )}
                      </span>

                      <span>
                        {formatDate(
                          execution.created_at ||
                            execution.timestamp ||
                            execution.started_at
                        )}
                      </span>
                    </div>
                  </div>

                  <div
                    className={`execution-badge ${getHistoryStatusClass(
                      execution.status
                    )}`}
                  >
                    <span className="status-dot" />

                    {safeRender(
                      execution.status,
                      "unknown"
                    )}
                  </div>

                  <div className="history-arrow">
                    →
                  </div>
                </button>
              )
            )}
          </div>
        )}
      </div>

      {selectedExecution && (
        <ExecutionDetails
          execution={
            selectedExecution
          }
          loading={
            detailsLoading
          }
          onClose={() =>
            setSelectedExecution(
              null
            )
          }
          onLoadInCommand={() => {
            onOpenExecution(
              selectedExecution
            );
          }}
        />
      )}
    </section>
  );
}


/* =========================================================
   EXECUTION DETAILS
========================================================= */

function ExecutionDetails({
  execution,
  loading,
  onClose,
  onLoadInCommand,
}) {
  const safeExecution =
    safeObject(execution);

  const tasks = useMemo(() => {
    if (
      Array.isArray(
        safeExecution.tasks
      )
    ) {
      return safeExecution.tasks.map(
        (task) =>
          safeObject(task)
      );
    }

    if (
      Array.isArray(
        safeExecution.plan
      )
    ) {
      const flattened = [];

      safeExecution.plan.forEach(
        (task) => {
          const subtasks =
            safeArray(
              task?.subtasks
            );

          if (
            subtasks.length
          ) {
            subtasks.forEach(
              (subtask) =>
                flattened.push(
                  safeObject(
                    subtask
                  )
                )
            );
          } else {
            flattened.push(
              safeObject(task)
            );
          }
        }
      );

      return flattened;
    }

    return [];
  }, [safeExecution]);

  const completed =
    tasks.filter(
      (task) =>
        task.status ===
        "completed"
    ).length;

  const progress =
    tasks.length > 0
      ? Math.round(
          (completed /
            tasks.length) *
            100
        )
      : safeExecution.status ===
        "completed"
      ? 100
      : 0;

  const finalResult =
    safeExecution.final_result ||
    safeExecution.result;

  const finalAnswer =
    getFinalAnswer(
      finalResult
    );

  const keyResults =
    safeArray(
      finalResult?.key_results
    );

  return (
    <div
      className="command-card"
      style={{
        marginTop: "24px",
      }}
    >
      <div className="command-header">
        <div>
          <div className="section-kicker">
            EXECUTION DETAILS
          </div>

          <h3>
            {safeRender(
              safeExecution.goal,
              "Execution"
            )}
          </h3>
        </div>

        <button
          className="clear-button"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      {loading && (
        <div className="result-summary">
          Loading complete execution
          details...
        </div>
      )}

      <div className="execution-info">
        <div className="info-row">
          <span>
            Status
          </span>

          <strong>
            {safeRender(
              safeExecution.status,
              "Unknown"
            )}
          </strong>
        </div>

        <div className="info-row">
          <span>
            Execution ID
          </span>

          <strong>
            {safeRender(
              safeExecution.execution_id ||
                safeExecution.id
            )}
          </strong>
        </div>

        <div className="info-row">
          <span>
            Tasks
          </span>

          <strong>
            {tasks.length}
          </strong>
        </div>

        <div className="info-row">
          <span>
            Progress
          </span>

          <strong>
            {progress}%
          </strong>
        </div>
      </div>

      <div
        className="progress-container"
        style={{
          marginTop: "24px",
        }}
      >
        <div className="progress-label">
          <span>
            Execution progress
          </span>

          <strong>
            {progress}%
          </strong>
        </div>

        <div className="progress-track">
          <div
            className="progress-fill"
            style={{
              width: `${progress}%`,
            }}
          />
        </div>
      </div>

      {tasks.length > 0 && (
        <div
          className="task-list"
          style={{
            marginTop: "24px",
          }}
        >
          {tasks.map(
            (
              task,
              index
            ) => (
              <div
                className="task-row"
                key={
                  safeText(
                    task.id,
                    `${index}-${safeText(
                      task.description
                    )}`
                  )
                }
              >
                <div
                  className={`task-number ${
                    task.status ===
                    "completed"
                      ? "task-complete"
                      : ""
                  }`}
                >
                  {task.status ===
                  "completed"
                    ? "✓"
                    : index + 1}
                </div>

                <div className="task-content">
                  <div className="task-title">
                    {safeRender(
                      task.description,
                      "Unnamed task"
                    )}
                  </div>

                  <div className="task-meta">
                    Task ID:{" "}
                    {safeRender(
                      task.id
                    )}

                    {task.priority !==
                      undefined &&
                      task.priority !==
                        null && (
                        <>
                          {" • Priority: "}
                          {safeRender(
                            task.priority
                          )}
                        </>
                      )}
                  </div>
                </div>

                <div
                  className={
                    task.status ===
                    "completed"
                      ? "task-status task-status-complete"
                      : task.status ===
                        "failed"
                      ? "task-status task-status-failed"
                      : "task-status task-status-pending"
                  }
                >
                  {safeRender(
                    task.status,
                    "pending"
                  )}
                </div>
              </div>
            )
          )}
        </div>
      )}

      {finalResult && (
        <div
          className="result-card"
          style={{
            marginTop: "24px",
          }}
        >
          <div className="section-kicker">
            FINAL RESULT
          </div>

          <h3>
            Objective Outcome
          </h3>

          <div
            className="result-summary"
            style={{
              fontSize:
                "16px",
              lineHeight:
                "1.7",
              fontWeight:
                600,
              whiteSpace:
                "pre-wrap",
            }}
          >
            {finalAnswer ||
              "AURA completed the execution pipeline."}
          </div>

          {keyResults.length >
            0 && (
            <div
              className="result-summary"
              style={{
                marginTop:
                  "16px",
              }}
            >
              <div className="section-kicker">
                KEY RESULTS
              </div>

              {keyResults.map(
                (
                  item,
                  index
                ) => (
                  <div
                    key={
                      index
                    }
                    style={{
                      marginTop:
                        "10px",
                    }}
                  >
                    {formatKeyResult(
                      item
                    )}
                  </div>
                )
              )}
            </div>
          )}
        </div>
      )}

      <div
        style={{
          display:
            "flex",
          justifyContent:
            "flex-end",
          marginTop:
            "20px",
        }}
      >
        <button
          className="execute-button"
          onClick={
            onLoadInCommand
          }
        >
          Open in Command
          Center

          <span className="button-arrow">
            →
          </span>
        </button>
      </div>
    </div>
  );
}


/* =========================================================
   MEMORY VIEW
========================================================= */

function MemoryView() {
  const [episodes, setEpisodes] =
    useState([]);

  const [facts, setFacts] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadMemory() {
    setLoading(true);
    setError("");

    try {
      const [
        episodeData,
        factData,
      ] = await Promise.all([
        import("./api").then(
          (module) =>
            module.getEpisodes()
        ),
        import("./api").then(
          (module) =>
            module.getFacts()
        ),
      ]);

      setEpisodes(
        safeArray(
          episodeData?.episodes ??
            episodeData
        )
      );

      setFacts(
        normalizeFacts(
          factData?.facts ??
            factData
        )
      );
    } catch (
      requestError
    ) {
      setError(
        safeText(
          requestError?.message,
          "Unable to load memory."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMemory();
  }, []);

  return (
    <section>
      <div className="command-card">
        <div className="command-header">
          <div>
            <div className="section-kicker">
              MEMORY
            </div>

            <h3>
              Persistent agent memory
            </h3>
          </div>

          <button
            className="clear-button"
            onClick={
              loadMemory
            }
            disabled={loading}
          >
            {loading
              ? "Loading..."
              : "Refresh"}
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <span>
              !
            </span>

            {safeRender(error)}
          </div>
        )}

        {!error && (
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon blue">
                ◎
              </div>

              <div>
                <div className="metric-value">
                  {episodes.length}
                </div>

                <div className="metric-label">
                  EPISODES
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon purple">
                ◇
              </div>

              <div>
                <div className="metric-value">
                  {facts.length}
                </div>

                <div className="metric-label">
                  FACTS
                </div>
              </div>
            </div>
          </div>
        )}

        {!loading &&
          episodes.length ===
            0 &&
          facts.length ===
            0 &&
          !error && (
            <div className="result-summary">
              No persistent memory
              has been stored yet.
            </div>
          )}

        {episodes.length >
          0 && (
          <div
            className="task-list"
            style={{
              marginTop:
                "20px",
            }}
          >
            {episodes
              .slice(0, 10)
              .map(
                (
                  episode,
                  index
                ) => (
                  <div
                    className="task-row"
                    key={
                      safeText(
                        episode?.id,
                        index
                      )
                    }
                  >
                    <div className="task-number">
                      E
                    </div>

                    <div className="task-content">
                      <div className="task-title">
                        {safeRender(
                          episode?.goal ||
                            episode?.description ||
                            episode?.content ||
                            episode?.result,
                          "Episode"
                        )}
                      </div>

                      <div className="task-meta">
                        Episodic memory
                      </div>
                    </div>
                  </div>
                )
              )}
          </div>
        )}
      </div>

      {facts.length >
        0 && (
        <div
          className="command-card"
          style={{
            marginTop:
              "24px",
          }}
        >
          <div className="section-kicker">
            SEMANTIC MEMORY
          </div>

          <h3>
            Learned facts
          </h3>

          <div className="task-list">
            {facts
              .slice(0, 10)
              .map(
                (
                  fact,
                  index
                ) => (
                  <div
                    className="task-row"
                    key={
                      safeText(
                        fact?.id ||
                          fact?.key,
                        index
                      )
                    }
                  >
                    <div className="task-number">
                      F
                    </div>

                    <div className="task-content">
                      <div className="task-title">
                        {safeRender(
                          fact?.key,
                          "Stored fact"
                        )}
                      </div>

                      <div className="task-meta">
                        {formatFactValue(
                          fact?.value ??
                            fact?.fact ??
                            fact?.content
                        )}
                      </div>
                    </div>
                  </div>
                )
              )}
          </div>
        </div>
      )}
    </section>
  );
}


/* =========================================================
   HUMAN INTERVENTION PANEL
========================================================= */

function InterventionPanel({
  result,
  setResult,
}) {
  const [requests, setRequests] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [message, setMessage] =
    useState("");

  async function loadRequests() {
    setLoading(true);
    setMessage("");

    try {
      const data =
        await getPendingInterventions();

      setRequests(
        safeArray(
          data?.requests
        )
      );
    } catch (
      requestError
    ) {
      setMessage(
        safeText(
          requestError?.message,
          "Unable to load interventions."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRequests();
  }, []);

  async function handleApprove(
    taskId
  ) {
    try {
      await approveIntervention(
        taskId
      );

      setMessage(
        "Intervention approved."
      );

      await loadRequests();
    } catch (
      requestError
    ) {
      setMessage(
        safeText(
          requestError?.message,
          "Approval failed."
        )
      );
    }
  }

  async function handleReject(
    taskId
  ) {
    try {
      await rejectIntervention(
        taskId
      );

      setMessage(
        "Intervention rejected."
      );

      await loadRequests();
    } catch (
      requestError
    ) {
      setMessage(
        safeText(
          requestError?.message,
          "Rejection failed."
        )
      );
    }
  }

  async function handleResume(
    request
  ) {
    try {
      setLoading(true);

      const resumed =
        await resumeIntervention(
          request.task_id,
          request.task_description
        );

      setResult(
        (previous) => ({
          ...(previous ||
            {}),
          ...safeObject(
            resumed
          ),
        })
      );

      setMessage(
        resumed?.success
          ? "Execution resumed successfully."
          : "Execution resume completed with an issue."
      );

      await loadRequests();
    } catch (
      requestError
    ) {
      setMessage(
        safeText(
          requestError?.message,
          "Unable to resume execution."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="command-card">
      <div className="command-header">
        <div>
          <div className="section-kicker">
            HUMAN INTERVENTION
          </div>

          <h3>
            Approval required
          </h3>
        </div>

        <button
          className="clear-button"
          onClick={
            loadRequests
          }
          disabled={loading}
        >
          {loading
            ? "Loading..."
            : "Refresh"}
        </button>
      </div>

      {message && (
        <div className="result-summary">
          {safeRender(
            message
          )}
        </div>
      )}

      {requests.length ===
      0 ? (
        <div className="result-summary">
          No pending intervention
          requests.
        </div>
      ) : (
        <div
          className="task-list"
          style={{
            marginTop:
              "18px",
          }}
        >
          {requests.map(
            (
              request,
              index
            ) => (
              <div
                className="task-row"
                key={
                  safeText(
                    request?.task_id,
                    index
                  )
                }
              >
                <div className="task-number">
                  !
                </div>

                <div className="task-content">
                  <div className="task-title">
                    {safeRender(
                      request?.task_description,
                      "Intervention request"
                    )}
                  </div>

                  <div className="task-meta">
                    {safeRender(
                      request?.category,
                      "approval"
                    )}{" "}
                    • Task{" "}
                    {safeRender(
                      request?.task_id
                    )}
                  </div>
                </div>

                <button
                  className="clear-button"
                  onClick={() =>
                    handleApprove(
                      request.task_id
                    )
                  }
                >
                  Approve
                </button>

                <button
                  className="clear-button"
                  onClick={() =>
                    handleReject(
                      request.task_id
                    )
                  }
                >
                  Reject
                </button>

                {request.status ===
                  "approved" && (
                  <button
                    className="execute-button"
                    onClick={() =>
                      handleResume(
                        request
                      )
                    }
                  >
                    Resume
                  </button>
                )}
              </div>
            )
          )}
        </div>
      )}

      {result?.status ===
        "waiting_for_human" && (
        <div className="result-summary">
          The previous AURA execution
          is waiting for human
          approval. Approve the
          required task and resume
          execution.
        </div>
      )}
    </section>
  );
}


/* =========================================================
   NORMALIZE SAVED EXECUTION
========================================================= */

function normalizeExecutionResult(
  execution
) {
  const source =
    safeObject(execution);

  const finalResult =
    source.final_result ||
    source.result ||
    null;

  return {
    ...source,

    success:
      source.success ??
      source.status ===
        "completed",

    execution_id:
      safeText(
        source.execution_id
      ),

    status:
      safeText(
        source.status,
        "completed"
      ),

    plan:
      Array.isArray(
        source.plan
      )
        ? source.plan
        : buildPlanFromTasks(
            source.tasks
          ),

    final_result:
      normalizeFinalResult(
        finalResult
      ),

    verification:
      safeArray(
        source.verification
      ),

    memory:
      safeObject(
        source.memory
      ),

    execution_state:
      safeObject(
        source.execution_state
      ),
  };
}


/* =========================================================
   NORMALIZE FINAL RESULT
========================================================= */

function normalizeFinalResult(
  value
) {
  if (
    value === null ||
    value === undefined
  ) {
    return {
      answer: "",
      summary: "",
      key_results: [],
    };
  }

  if (
    typeof value ===
      "string" ||
    typeof value ===
      "number"
  ) {
    return {
      answer: String(
        value
      ),
      summary: String(
        value
      ),
      key_results: [],
    };
  }

  if (
    typeof value !==
      "object"
  ) {
    return {
      answer: String(
        value
      ),
      summary: String(
        value
      ),
      key_results: [],
    };
  }

  const normalized = {
    ...value,
  };

  if (
    value.answer !==
      undefined
  ) {
    normalized.answer =
      safeText(
        value.answer
      );
  }

  if (
    value.summary !==
      undefined
  ) {
    normalized.summary =
      safeText(
        value.summary
      );
  }

  if (
    value.message !==
      undefined
  ) {
    normalized.message =
      safeText(
        value.message
      );
  }

  if (
    value.result !==
      undefined &&
    typeof value.result !==
      "object"
  ) {
    normalized.result =
      safeText(
        value.result
      );
  }

  normalized.key_results =
    safeArray(
      value.key_results
    ).map(
      (item) => {
        if (
          !item ||
          typeof item !==
            "object"
        ) {
          return {
            type:
              "generic",
            value:
              safeText(item),
          };
        }

        return {
          ...item,

          type:
            safeText(
              item.type,
              "generic"
            ),

          expression:
            safeText(
              item.expression
            ),

          result:
            safeText(
              item.result
            ),

          query:
            safeText(
              item.query
            ),

          title:
            safeText(
              item.title
            ),

          url:
            safeText(
              item.url
            ),

          result_count:
            safeText(
              item.result_count
            ),
        };
      }
    );

  return normalized;
}


/* =========================================================
   BUILD PLAN FROM TASKS
========================================================= */

function buildPlanFromTasks(
  tasks
) {
  if (
    !Array.isArray(tasks)
  ) {
    return [];
  }

  return [
    {
      id: 1,

      description:
        "Saved execution tasks",

      status:
        "completed",

      subtasks:
        tasks.map(
          (task) =>
            safeObject(
              task
            )
        ),
    },
  ];
}


/* =========================================================
   SEMANTIC MEMORY HELPERS
========================================================= */

function normalizeFacts(
  data
) {
  if (!data) {
    return [];
  }

  if (
    Array.isArray(data)
  ) {
    return data.map(
      (item) =>
        safeObject(item)
    );
  }

  if (
    typeof data ===
      "object"
  ) {
    return Object.entries(
      data
    ).map(
      ([key, value]) => {
        if (
          value &&
          typeof value ===
            "object" &&
          !Array.isArray(
            value
          ) &&
          "value" in value
        ) {
          return {
            key,

            value:
              value.value,

            timestamp:
              value.timestamp,
          };
        }

        return {
          key,
          value,
        };
      }
    );
  }

  return [];
}


function formatFactValue(
  value
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "";
  }

  if (
    typeof value ===
      "string"
  ) {
    return value;
  }

  if (
    typeof value ===
      "number" ||
    typeof value ===
      "boolean"
  ) {
    return String(
      value
    );
  }

  try {
    return JSON.stringify(
      value,
      null,
      2
    );
  } catch {
    return safeText(
      value
    );
  }
}


export default App;