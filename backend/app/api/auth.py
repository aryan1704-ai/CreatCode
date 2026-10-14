import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_db,
)
from models import User, Project

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")


def validate_email_format(email: str) -> str:
    cleaned = email.strip().lower()
    if not EMAIL_REGEX.match(cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address"
        )
    return cleaned


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return validate_email_format(v)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return validate_email_format(v)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    normalized_email = request.email

    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists"
        )

    hashed_pw = hash_password(request.password)

    new_user = User(
        name=request.name.strip(),
        email=normalized_email,
        password_hash=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Automatically initialize a starter project for the new user
    starter_project = Project(
        user_id=new_user.id,
        name="My First Project",
        description="Default project created for your code workspace"
    )
    db.add(starter_project)
    db.commit()
    db.refresh(starter_project)

    token = create_access_token({"sub": str(new_user.id), "email": new_user.email})

    return {
        "status": "success",
        "message": "Account created successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    normalized_email = request.email

    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})

    return {
        "status": "success",
        "message": "Logged in successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": current_user.created_at
        }
    }


@router.post("/logout")
def logout():
    return {
        "status": "success",
        "message": "Logged out successfully"
    }
