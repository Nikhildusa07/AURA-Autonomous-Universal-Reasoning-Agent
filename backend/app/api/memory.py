from fastapi import APIRouter

from backend.app.memory.memory import memory


router = APIRouter(
    prefix="/memory",
    tags=["Memory"]
)


@router.get("/episodes")
def get_episodes():
    return {
        "count": len(memory.get_episodes()),
        "episodes": memory.get_episodes()
    }


@router.get("/facts")
def get_facts():
    return {
        "count": len(memory.get_all_facts()),
        "facts": memory.get_all_facts()
    }