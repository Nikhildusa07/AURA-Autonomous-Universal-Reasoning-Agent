from fastapi import APIRouter, HTTPException

from backend.app.memory.execution_memory import (
    execution_memory
)


router = APIRouter(
    prefix="/executions",
    tags=["Executions"]
)


@router.get("")
def get_all_executions():
    executions = execution_memory.get_all_executions()

    return {
        "success": True,
        "count": len(executions),
        "executions": executions
    }


@router.get("/pending")
def get_pending_executions():
    executions = (
        execution_memory.get_pending_executions()
    )

    return {
        "success": True,
        "count": len(executions),
        "executions": executions
    }


@router.get("/{execution_id}")
def get_execution(execution_id: str):
    execution = execution_memory.get_execution(
        execution_id
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found."
        )

    return {
        "success": True,
        "execution": execution
    }


@router.delete("/{execution_id}")
def delete_execution(execution_id: str):
    deleted = execution_memory.delete_execution(
        execution_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Execution not found."
        )

    return {
        "success": True,
        "execution_id": execution_id,
        "message": "Execution deleted successfully."
    }