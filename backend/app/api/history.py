from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user, get_db
from models import CodeGeneration, Project, User


router = APIRouter(
    prefix="/api/history",
    tags=["Code History"]
)


@router.get("/")
def get_all_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch all project IDs owned by this user
    user_project_ids = [
        p.id for p in db.query(Project.id).filter(Project.user_id == current_user.id).all()
    ]

    generations = (
        db.query(CodeGeneration)
        .filter(
            (CodeGeneration.user_id == current_user.id) |
            (CodeGeneration.project_id.in_(user_project_ids))
        )
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


@router.get("/project/{project_id}")
def get_project_history(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user owns the project
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized access"
        )

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


@router.get("/{generation_id}")
def get_generation(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    generation = (
        db.query(CodeGeneration)
        .filter(CodeGeneration.id == generation_id)
        .first()
    )

    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Code generation record not found"
        )

    # Check ownership
    is_owner = False
    if generation.user_id == current_user.id:
        is_owner = True
    elif generation.project_id:
        proj = (
            db.query(Project)
            .filter(Project.id == generation.project_id, Project.user_id == current_user.id)
            .first()
        )
        if proj:
            is_owner = True

    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this history item"
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


@router.delete("/{generation_id}")
def delete_generation(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    generation = (
        db.query(CodeGeneration)
        .filter(CodeGeneration.id == generation_id)
        .first()
    )

    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Code generation record not found"
        )

    # Check ownership
    is_owner = False
    if generation.user_id == current_user.id:
        is_owner = True
    elif generation.project_id:
        proj = (
            db.query(Project)
            .filter(Project.id == generation.project_id, Project.user_id == current_user.id)
            .first()
        )
        if proj:
            is_owner = True

    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to delete this history item"
        )

    db.delete(generation)
    db.commit()

    return {
        "status": "success",
        "message": "Code history deleted successfully"
    }