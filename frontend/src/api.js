const API_BASE_URL = "https://aura-autonomous-universal-reasoning-agent.onrender.com";

/* =========================================================
   AGENT
========================================================= */

export async function runAgent(goal) {
  const response = await fetch(`${API_BASE_URL}/agent/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      goal: goal.trim(),
    }),
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        `Agent request failed (${response.status}).`
    );
  }

  return data;
}

/* =========================================================
   EXECUTION HISTORY
========================================================= */

export async function getExecutions() {
  const response = await fetch(`${API_BASE_URL}/executions`);

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        "Failed to load execution history."
    );
  }

  return data;
}

/* =========================================================
   SINGLE EXECUTION
========================================================= */

export async function getExecution(executionId) {
  if (!executionId) {
    throw new Error("Execution ID is required.");
  }

  const response = await fetch(
    `${API_BASE_URL}/executions/${encodeURIComponent(executionId)}`
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        "Failed to load execution details."
    );
  }

  return data;
}

/* =========================================================
   EPISODIC MEMORY
========================================================= */

export async function getEpisodes() {
  const response = await fetch(
    `${API_BASE_URL}/memory/episodes`
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        "Failed to load episodic memory."
    );
  }

  return data;
}

/* =========================================================
   SEMANTIC MEMORY
========================================================= */

export async function getFacts() {
  const response = await fetch(
    `${API_BASE_URL}/memory/facts`
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        "Failed to load semantic memory."
    );
  }

  return data;
}

/* =========================================================
   HUMAN INTERVENTION
========================================================= */

export async function getPendingInterventions() {
  const response = await fetch(
    `${API_BASE_URL}/intervention/pending`
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        "Failed to load pending interventions."
    );
  }

  return data;
}

/* =========================================================
   APPROVE INTERVENTION
========================================================= */

export async function approveIntervention(
  taskId,
  responseText = "Approved by human."
) {
  const response = await fetch(
    `${API_BASE_URL}/intervention/${taskId}/approve`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        response: responseText,
      }),
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        "Failed to approve intervention."
    );
  }

  return data;
}

/* =========================================================
   REJECT INTERVENTION
========================================================= */

export async function rejectIntervention(
  taskId,
  responseText = "Rejected by human."
) {
  const response = await fetch(
    `${API_BASE_URL}/intervention/${taskId}/reject`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        response: responseText,
      }),
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        "Failed to reject intervention."
    );
  }

  return data;
}

/* =========================================================
   RESUME INTERVENTION
========================================================= */

export async function resumeIntervention(
  taskId,
  taskDescription
) {
  const response = await fetch(
    `${API_BASE_URL}/intervention/resume`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        task_id: taskId,
        task_description: taskDescription,
      }),
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Backend returned an invalid response (${response.status}).`
    );
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.error ||
        "Failed to resume execution."
    );
  }

  return data;
}

/* =========================================================
   DEFAULT EXPORT
========================================================= */

export default {
  runAgent,
  getExecutions,
  getExecution,
  getEpisodes,
  getFacts,
  getPendingInterventions,
  approveIntervention,
  rejectIntervention,
  resumeIntervention,
};