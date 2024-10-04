from fastapi import APIRouter, Depends

from app.dependencies import authorize, authorize_interview
from app.services.azure import AzureService
from app.types.azure_response import AzureResponse
from app.utils.errors import (
    BadRequestExceptionResponse,
    InternalServerErrorExceptionResponse,
)

router = APIRouter(
    prefix="/azure",
    tags=["Azure"],
    dependencies=[
        Depends(authorize),
        Depends(authorize_interview),
    ],
)

azure_service = AzureService()


@router.get(
    "/token",
    responses={**InternalServerErrorExceptionResponse, **BadRequestExceptionResponse},
)
async def token() -> AzureResponse:
    return azure_service.generate_token()
