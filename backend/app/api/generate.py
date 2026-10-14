from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_optional_current_user, get_db
from models import CodeGeneration, Project, User
from services.ai_service import generate_code


router = APIRouter(
    prefix="/api/generate",
    tags=["Code Generation"]
)


class GenerateRequest(BaseModel):
    prompt: str
    project_id: Optional[int] = None


@router.post("/")
def generate(
    request: GenerateRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    result = generate_code(request.prompt)

    try:
        user_id = current_user.id if current_user else None
        valid_project_id = None

        if request.project_id:
            # If user is logged in, verify ownership of the project
            if current_user:
                proj = (
                    db.query(Project)
                    .filter(
                        Project.id == request.project_id,
                        Project.user_id == current_user.id
                    )
                    .first()
                )
                if proj:
                    valid_project_id = proj.id
            else:
                # If guest, only attach if project exists
                proj = db.query(Project).filter(Project.id == request.project_id).first()
                if proj:
                    valid_project_id = proj.id

        generation = CodeGeneration(
            project_id=valid_project_id,
            user_id=user_id,
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

    except Exception as e:
        # If DB save fails for any reason, still return the generated code so user isn't blocked
        return {
            "status": "success",
            "generation_id": None,
            "result": result,
            "note": "Result generated, but history sync was skipped."
        }