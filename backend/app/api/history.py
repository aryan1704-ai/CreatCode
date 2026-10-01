from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import CodeGeneration


router = APIRouter(
    prefix="/api/history",
    tags=["Code History"]
)


@router.get("/")
def get_all_history():

    db: Session = SessionLocal()

    try:
        generations = (
            db.query(CodeGeneration)
            .order_by(CodeGeneration.created_at.desc())
            .all()
        )

        return {
            "status": "success",
            "history": [
                {
                    "id": item.id,
                    "project_id": item.project_id,
                    "prompt": item.prompt,
                    "generated_code": item.generated_code,
                    "language": item.language,
                    "action": item.action,
                    "created_at": item.created_at
                }
                for item in generations
            ]
        }

    finally:
        db.close()


@router.get("/project/{project_id}")
def get_project_history(project_id: int):

    db: Session = SessionLocal()

    try:
        generations = (
            db.query(CodeGeneration)
            .filter(CodeGeneration.project_id == project_id)
            .order_by(CodeGeneration.created_at.desc())
            .all()
        )

        return {
            "status": "success",
            "project_id": project_id,
            "history": [
                {
                    "id": item.id,
                    "prompt": item.prompt,
                    "generated_code": item.generated_code,
                    "language": item.language,
                    "action": item.action,
                    "created_at": item.created_at
                }
                for item in generations
            ]
        }

    finally:
        db.close()


@router.get("/{generation_id}")
def get_generation(generation_id: int):

    db: Session = SessionLocal()

    try:
        generation = (
            db.query(CodeGeneration)
            .filter(CodeGeneration.id == generation_id)
            .first()
        )

        if not generation:
            raise HTTPException(
                status_code=404,
                detail="Code generation not found"
            )

        return {
            "status": "success",
            "generation": {
                "id": generation.id,
                "project_id": generation.project_id,
                "prompt": generation.prompt,
                "generated_code": generation.generated_code,
                "language": generation.language,
                "action": generation.action,
                "created_at": generation.created_at
            }
        }

    finally:
        db.close()


@router.delete("/{generation_id}")
def delete_generation(generation_id: int):

    db: Session = SessionLocal()

    try:
        generation = (
            db.query(CodeGeneration)
            .filter(CodeGeneration.id == generation_id)
            .first()
        )

        if not generation:
            raise HTTPException(
                status_code=404,
                detail="Code generation not found"
            )

        db.delete(generation)
        db.commit()

        return {
            "status": "success",
            "message": "Code history deleted successfully"
        }

    finally:
        db.close()