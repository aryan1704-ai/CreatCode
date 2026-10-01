from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from models import User

from api.generate import router as generate_router
from api.explain import router as explain_router
from api.debug import router as debug_router
from api.optimize import router as optimize_router
from api.complexity import router as complexity_router
from api.testcases import router as testcases_router
from api.convert import router as convert_router
from api.prompt import router as prompt_router
from api.projects import router as projects_router
from api.history import router as history_router
from api.users import router as users_router
from api.chat import router as chat_router
from api.run import router as run_router

# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="CreatCode API",
    description="AI Code Generator and Explainer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "null",
    "https://creatcode.onrender.com",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RuntimeError)
async def runtime_error_handler(
    request: Request,
    exc: RuntimeError
):
    return JSONResponse(
        status_code=503,
        content={
            "status": "error",
            "message": str(exc)
        }
    )


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to CreatCode API",
        "status": "success"
    }


# Health check endpoint
@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "service": "CreatCode API",
            "database": "connected"
        }

    except Exception as error:
        return {
            "status": "unhealthy",
            "service": "CreatCode API",
            "database": "disconnected",
            "error": str(error)
        }


# Include API routers
app.include_router(generate_router)
app.include_router(explain_router)
app.include_router(debug_router)
app.include_router(optimize_router)
app.include_router(complexity_router)
app.include_router(testcases_router)
app.include_router(convert_router)
app.include_router(prompt_router)
app.include_router(projects_router)
app.include_router(history_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(run_router)