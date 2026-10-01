from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import generate_prompt


router = APIRouter(
    prefix="/api/prompt",
    tags=["Prompt Generator"]
)


class PromptRequest(BaseModel):
    requirement: str


@router.post("/")
def create_prompt(request: PromptRequest):
    result = generate_prompt(request.requirement)

    return {
        "status": "success",
        "prompt": result
    }