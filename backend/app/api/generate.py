from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import CodeGeneration
from services.ai_service import generate_code


router = APIRouter(
    prefix="/api/generate",
    tags=["Code Generation"]
)


class GenerateRequest(BaseModel):
    prompt: str
    project_id: int = 1


@router.post("/")
def generate(request: GenerateRequest):

    result = generate_code(request.prompt)

    db: Session = SessionLocal()

    try:
        generation = CodeGeneration(
            project_id=request.project_id,
            prompt=request.prompt,
            generated_code=result,
            language="auto",
            action="generate"
        )

        db.add(generation)
        db.commit()
        db.refresh(generation)

        return {
            "status": "success",
            "generation_id": generation.id,
            "result": result
        }

    finally:
        db.close()