from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.core.intervention_manager import (
    intervention_manager
)
from backend.app.core.intervention_resume import (
    intervention_resume
)


router = APIRouter(
    prefix="/intervention",
    tags=["Human Intervention"]
)


class InterventionResponse(BaseModel):
    response: str = "Approved by human."


class InterventionResumeRequest(BaseModel):
    task_id: int
    task_description: str


@router.get("/pending")
def get_pending_interventions():
    return {
        "success": True,
        "count": len(
            intervention_manager.get_pending()
        ),
        "requests":
            intervention_manager.get_pending()
    }


@router.get("/all")
def get_all_interventions():
    from backend.app.core.human_intervention import (
        human_intervention
    )

    requests = (
        human_intervention.get_all_requests()
    )

    return {
        "success": True,
        "count": len(requests),
        "requests": requests
    }


@router.post("/{task_id}/approve")
def approve_intervention(
    task_id: int,
    request: InterventionResponse
):
    result = intervention_manager.approve(
        task_id=task_id,
        response=request.response
    )

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result


@router.post("/{task_id}/reject")
def reject_intervention(
    task_id: int,
    request: InterventionResponse
):
    result = intervention_manager.reject(
        task_id=task_id,
        response=request.response
    )

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result


@router.post("/resume")
def resume_intervention(
    request: InterventionResumeRequest
):
    result = intervention_resume.resume(
        task_id=request.task_id,
        task_description=request.task_description
    )

    if not result["success"]:

        status = result.get(
            "status",
            "failed"
        )

        if status == "not_found":
            status_code = 404
        elif status in (
            "pending",
            "rejected"
        ):
            status_code = 409
        else:
            status_code = 500

        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return result