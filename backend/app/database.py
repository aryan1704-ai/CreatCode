import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Use DATABASE_URL if provided.
# Otherwise, use SQLite.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./creatcode.db"
)

# SQLite needs this option when used with FastAPI.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=True
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()