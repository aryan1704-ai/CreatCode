from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import debug_code


router = APIRouter(
    prefix="/api/debug",
    tags=["Code Debugging"]
)


class DebugRequest(BaseModel):
    code: str
    error: str = ""


@router.post("/")
def debug(request: DebugRequest):

    result = debug_code(
        request.code,
        request.error
    )

    return {
        "status": "success",
        "debug_result": result
    }