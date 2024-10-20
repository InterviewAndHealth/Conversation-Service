from fastapi import APIRouter, Depends

from app.dependencies import authorize, authorize_interview
from app.services.aws import AwsService
from app.types.aws_response import AwsResponse
from app.utils.errors import BadRequestResponse, InternalServerErrorResponse

router = APIRouter(
    prefix="/aws",
    tags=["AWS"],
    dependencies=[
        Depends(authorize),
        Depends(authorize_interview),
    ],
)

aws_service = AwsService()


@router.get(
    "/credentials",
    responses={**InternalServerErrorResponse, **BadRequestResponse},
)
async def credentials(interview_id: str) -> AwsResponse:
    return aws_service.generate_credentials(interview_id)
