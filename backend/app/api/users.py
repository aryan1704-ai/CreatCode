import re
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from typing import Optional

from auth import get_current_user, get_db, hash_password
from models import User


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    @field_validator("email")
    @classmethod
    def check_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip().lower()
            if not EMAIL_REGEX.match(cleaned):
                raise ValueError("Invalid email format")
            return cleaned
        return v


@router.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": current_user.created_at
        }
    }


@router.put("/me")
def update_current_user_profile(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if request.name:
        current_user.name = request.name.strip()

    if request.email:
        normalized_email = request.email.strip().lower()
        if normalized_email != current_user.email:
            existing = db.query(User).filter(User.email == normalized_email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already in use by another account"
                )
            current_user.email = normalized_email

    if request.password:
        if len(request.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        current_user.password_hash = hash_password(request.password)

    db.commit()
    db.refresh(current_user)

    return {
        "status": "success",
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        }
    }


@router.get("/{user_id}")
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow retrieving own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this profile"
        )

    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": current_user.created_at
        }
    }