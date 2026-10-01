from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import explain_code


router = APIRouter(
    prefix="/api/explain",
    tags=["Code Explanation"]
)


class ExplainRequest(BaseModel):
    code: str


@router.post("/")
def explain(request: ExplainRequest):

    result = explain_code(request.code)

    return {
        "status": "success",
        "explanation": result
    }