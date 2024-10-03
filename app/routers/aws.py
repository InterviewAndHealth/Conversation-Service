from fastapi import APIRouter, Depends

from app.dependencies import authorize, authorize_interview
from app.services.aws import AwsService
from app.types.aws_response import AwsResponse

router = APIRouter(
    prefix="/aws",
    tags=["AWS"],
    dependencies=[
        Depends(authorize),
        Depends(authorize_interview),
    ],
)

aws_service = AwsService()


@router.get("/transcribe")
async def transcribe() -> AwsResponse:
    return aws_service.transcribe()


@router.get("/polly")
async def polly(text: str) -> AwsResponse:
    return aws_service.polly(text)
