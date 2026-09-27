from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.agent import router as agent_router
from backend.app.api.memory import router as memory_router
from backend.app.api.intervention import (
    router as intervention_router
)
from backend.app.api.execution import (
    router as execution_router

)
from backend.app.api.evaluation import router as evaluation_router
from backend.app.memory.database import initialize_database


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

initialize_database()


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AURA",
    description="Autonomous Universal Reasoning Agent",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://aura-bay-pi.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(agent_router)
app.include_router(memory_router)
app.include_router(intervention_router)
app.include_router(execution_router)
app.include_router(evaluation_router)

# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "AURA is running",
        "status": "online"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }