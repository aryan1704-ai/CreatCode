from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str
    email: str


@router.post("/")
def create_user(request: UserCreate):

    db: Session = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )

        user = User(
            name=request.name,
            email=request.email
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "status": "success",
            "message": "User created successfully",
            "user_id": user.id,
            "name": user.name,
            "email": user.email
        }

    finally:
        db.close()


@router.get("/")
def get_users():

    db: Session = SessionLocal()

    try:
        users = db.query(User).all()

        return {
            "status": "success",
            "users": [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at
                }
                for user in users
            ]
        }

    finally:
        db.close()


@router.get("/{user_id}")
def get_user(user_id: int):

    db: Session = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return {
            "status": "success",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at
            }
        }

    finally:
        db.close()


@router.put("/{user_id}")
def update_user(
    user_id: int,
    request: UserUpdate
):

    db: Session = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user.name = request.name
        user.email = request.email

        db.commit()
        db.refresh(user)

        return {
            "status": "success",
            "message": "User updated successfully",
            "user_id": user.id
        }

    finally:
        db.close()


@router.delete("/{user_id}")
def delete_user(user_id: int):

    db: Session = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        db.delete(user)
        db.commit()

        return {
            "status": "success",
            "message": "User deleted successfully"
        }

    finally:
        db.close()