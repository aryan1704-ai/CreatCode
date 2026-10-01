from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Project


router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


class ProjectCreate(BaseModel):
    user_id: int = 1
    name: str
    description: str = ""


class ProjectUpdate(BaseModel):
    name: str
    description: str = ""


@router.post("/")
def create_project(request: ProjectCreate):

    db: Session = SessionLocal()

    try:
        project = Project(
            user_id=request.user_id,
            name=request.name,
            description=request.description
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return {
            "status": "success",
            "message": "Project created successfully",
            "project_id": project.id,
            "name": project.name
        }

    finally:
        db.close()


@router.get("/")
def get_projects():

    db: Session = SessionLocal()

    try:
        projects = db.query(Project).all()

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

    finally:
        db.close()


@router.get("/{project_id}")
def get_project(project_id: int):

    db: Session = SessionLocal()

    try:
        project = db.query(Project).filter(
            Project.id == project_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
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

    finally:
        db.close()


@router.put("/{project_id}")
def update_project(
    project_id: int,
    request: ProjectUpdate
):

    db: Session = SessionLocal()

    try:
        project = db.query(Project).filter(
            Project.id == project_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        project.name = request.name
        project.description = request.description

        db.commit()
        db.refresh(project)

        return {
            "status": "success",
            "message": "Project updated successfully",
            "project_id": project.id
        }

    finally:
        db.close()


@router.delete("/{project_id}")
def delete_project(project_id: int):

    db: Session = SessionLocal()

    try:
        project = db.query(Project).filter(
            Project.id == project_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        db.delete(project)
        db.commit()

        return {
            "status": "success",
            "message": "Project deleted successfully"
        }

    finally:
        db.close()