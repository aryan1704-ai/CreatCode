from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import optimize_code


router = APIRouter(
    prefix="/api/optimize",
    tags=["Code Optimization"]
)


class OptimizeRequest(BaseModel):
    code: str


@router.post("/")
def optimize(request: OptimizeRequest):

    result = optimize_code(request.code)

    return {
        "status": "success",
        "optimization": result
    }