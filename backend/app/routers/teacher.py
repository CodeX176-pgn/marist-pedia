# This router will contain teacher/admin endpoints.
# For now, we are only creating the structure.
# Authentication and real permission checks will be added later.

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/teacher",
    tags=["Teacher"],
)


@router.get("/status")
async def teacher_status():
    """
    Simple endpoint used to verify that the teacher router
    is correctly registered with FastAPI.
    """

    return {
        "status": "ok",
        "area": "teacher",
    }
