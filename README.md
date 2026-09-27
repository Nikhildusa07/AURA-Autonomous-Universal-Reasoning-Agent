# AURA

**Autonomous Universal Reasoning Agent** is a local full-stack agent application. AURA turns a natural-language goal into a plan, chooses tools to carry out the work, verifies results, and records execution and memory data.

The project contains a FastAPI backend and a React 19 frontend built with Vite. The frontend provides views for agent commands, execution history, memory, human intervention, and benchmark evaluation.

## Features

- Gemini-backed task planning and result generation.
- Tool selection and execution for calculations, web research, and webpage reading.
- Execution context, task verification, retry/recovery, and replanning components.
- Persistent episodic memory, semantic facts, executions, and intervention requests in SQLite.
- Human approval/rejection and task-resume endpoints.
- A dashboard with six built-in evaluation benchmarks and evaluation reports.

## Requirements

- Python 3.10 or newer.
- Node.js 20.19+ or 22.12+ and npm (required by Vite 7).
- A Gemini API key for agent planning and generation.
- Internet access for Gemini requests, web searches, and webpage retrieval.

## Setup

Run these commands from the project root in PowerShell. The Python virtual environment and frontend dependencies are installed separately.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root with your Gemini credentials:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
```

`GEMINI_MODEL` is optional; if omitted, the backend uses `gemini-3.8-flash`. Keep the real API key private and do not commit `.env`.

Install frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

## Run Locally

Start the backend from the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Start the frontend in a second terminal:

```powershell
cd frontend
npm run dev
```

Open the Vite URL printed in the frontend terminal (normally `http://localhost:5173`). The backend listens at `http://127.0.0.1:8000`.

Useful backend URLs:

- `http://127.0.0.1:8000/` — service status.
- `http://127.0.0.1:8000/health` — health check.
- `http://127.0.0.1:8000/docs` — interactive API documentation.
- `http://127.0.0.1:8000/openapi.json` — OpenAPI schema.

The database is initialized automatically at `backend/app/memory/aura_memory.db` when the backend starts. Back up this file if you need to preserve local memory and execution history.

## Project Layout

```text
backend/app/
	ai/          Gemini integration, planning, and tool selection
	api/         FastAPI route handlers
	core/        Agent orchestration, execution, verification, and recovery
	evaluation/  Built-in benchmarks and evaluation logic
	memory/      SQLite persistence and memory services
	models/      Shared task models
	tools/       Calculator, web research, and browser tools
	main.py      FastAPI application and router registration
frontend/
	src/         React application, API client, and evaluation dashboard
	index.html   Vite HTML entry point
tests/         Currently empty; backend tests live beside their modules
```

## API Overview

The complete request and response schemas are available from `/docs` while the backend is running.

| Area | Routes |
| --- | --- |
| Agent | `POST /agent/run` |
| Health | `GET /`, `GET /health` |
| Executions | `GET /executions`, `GET /executions/pending`, `GET /executions/{execution_id}`, `DELETE /executions/{execution_id}` |
| Memory | `GET /memory/episodes`, `GET /memory/facts` |
| Human intervention | `GET /intervention/pending`, `GET /intervention/all`, `POST /intervention/{task_id}/approve`, `POST /intervention/{task_id}/reject`, `POST /intervention/resume` |
| Evaluation | `GET /evaluation/benchmarks`, `GET /evaluation/benchmarks/{benchmark_id}`, `POST /evaluation/run`, `POST /evaluation/record`, `GET /evaluation/report`, `GET /evaluation/results`, `DELETE /evaluation/results` |

## Tools and Integrations

- **Calculator:** evaluates supported arithmetic expressions locally.
- **Web research:** searches the web through `ddgs`.
- **Browser:** fetches HTTP/HTTPS pages with `requests` and extracts text and links with Beautiful Soup. It does not launch a graphical browser.
- **Gemini:** the backend reads `GEMINI_API_KEY` and optional `GEMINI_MODEL` from the process environment or root `.env` file.

## Tests and Build

Backend test modules are named `test_*.py` and are located throughout `backend/app/`; the top-level `tests/` directory is currently empty. `pytest` is not included in `requirements.txt`, so install it in the active virtual environment before running the tests:

```powershell
python -m pip install pytest
python -m pytest backend/app
```

Some tests exercise integrations and may need valid Gemini credentials or network access. Build the frontend with:

```powershell
cd frontend
npm run build
```

## Security and Scope

This is a local development application, not a production-hardened service. The API currently has no authentication or authorization. Do not expose it to an untrusted network, and keep Gemini credentials in the ignored `.env` file rather than source code.
