from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from auth import get_current_user, get_db
from models import Project, User, CodeGeneration


router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = ""


class ProjectUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = ""


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = Project(
        user_id=current_user.id,
        name=request.name.strip(),
        description=(request.description or "").strip()
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "status": "success",
        "message": "Project created successfully",
        "project_id": project.id,
        "name": project.name,
        "description": project.description
    }


@router.get("/")
def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.updated_at.desc(), Project.id.desc())
        .all()
    )

    return {
        "status": "success",
        "projects": [
            {
                "id": project.id,
                "user_id": project.user_id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }
            for project in projects
        ]
    }


@router.get("/{project_id}")
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    return {
        "status": "success",
        "project": {
            "id": project.id,
            "user_id": project.user_id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
    }


@router.put("/{project_id}")
def update_project(
    project_id: int,
    request: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    project.name = request.name.strip()
    project.description = (request.description or "").strip()

    db.commit()
    db.refresh(project)

    return {
        "status": "success",
        "message": "Project updated successfully",
        "project_id": project.id,
        "name": project.name,
        "description": project.description
    }


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    # Cascade delete any code generations associated with this project
    db.query(CodeGeneration).filter(CodeGeneration.project_id == project_id).delete()

    db.delete(project)
    db.commit()

    return {
        "status": "success",
        "message": "Project deleted successfully"
    }