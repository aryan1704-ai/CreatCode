from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import analyze_complexity

router = APIRouter(
    prefix="/api/complexity",
    tags=["Complexity Analysis"]
)


class ComplexityRequest(BaseModel):
    code: str


@router.post("/")
def complexity(request: ComplexityRequest):
    try:
        result = analyze_complexity(request.code)

        return {
            "status": "success",
            "analysis": result
        }

    except Exception as error:
        error_message = str(error)

        if "429" in error_message or "Rate limit" in error_message:
            return {
                "status": "rate_limited",
                "message": "Gemini API daily limit has been reached. Please try again later."
            }

        return {
            "status": "error",
            "message": "An error occurred while analyzing the code."
        }