from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import generate_test_cases


router = APIRouter(
    prefix="/api/testcases",
    tags=["Test Case Generator"]
)


class TestCaseRequest(BaseModel):
    code: str


@router.post("/")
def generate_test_cases_api(request: TestCaseRequest):
    result = generate_test_cases(request.code)

    return {
        "status": "success",
        "test_cases": result
    }