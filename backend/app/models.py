from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

class CodeGeneration(Base):
    __tablename__ = "code_generations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)

    prompt = Column(String(2000), nullable=False)
    generated_code = Column(String(10000), nullable=False)

    language = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False)

    created_at = Column(DateTime, server_default=func.now())