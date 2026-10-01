from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import convert_code


router = APIRouter(
    prefix="/api/convert",
    tags=["Code Conversion"]
)


class ConvertRequest(BaseModel):
    code: str
    target_language: str


@router.post("/")
def convert(request: ConvertRequest):
    result = convert_code(
        request.code,
        request.target_language
    )

    return {
        "status": "success",
        "converted_code": result
    }