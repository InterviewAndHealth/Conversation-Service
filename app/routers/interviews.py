from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import authorize
from app.services.chat import ChatService
from app.services.feedback import FeedbackService
from app.services.interview import InterviewService
from app.types.conversation_response import (
    ConversationResponse,
    InterviewDetailsResponse,
)
from app.types.interview_report_response import InterviewReportResponse
from app.types.message_request import MessageRequest
from app.types.message_response import MessageResponse
from app.utils.errors import (
    BadRequestException400,
    BadRequestResponse,
    InternalServerErrorException500,
    InternalServerErrorResponse,
    NotFoundException404,
    NotFoundResponse,
)
from app.utils.timer import timer

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "/start/{interview_id}",
    responses={
        **BadRequestResponse,
        **NotFoundResponse,
        **InternalServerErrorResponse,
    },
)
@timer
async def start_conversation(
    interview_id: str,
    user_id: Annotated[str, Depends(authorize)],
    is_job: bool = False,
) -> MessageResponse:
    interview_service = InterviewService(interview_id, user_id, is_job)
    if not await interview_service.initialize():
        raise InternalServerErrorException500()

    chat_service = ChatService(interview_id, user_id)

    if chat_service.is_active():
        raise BadRequestException400("Interview already started.")

    chat_service.set_active()
    await interview_service.publish_interview_started()
    return await chat_service.start()


@router.post(
    "/continue/{interview_id}",
    responses={**BadRequestResponse, **NotFoundResponse},
)
@timer
async def continue_conversation(
    interview_id: str,
    message: MessageRequest,
    user_id: Annotated[str, Depends(authorize)],
) -> MessageResponse:
    chat_service = ChatService(interview_id, user_id)
    return chat_service.invoke(message.message)


@router.post(
    "/end/{interview_id}", responses={**BadRequestResponse, **NotFoundResponse}
)
@timer
async def end_conversation(
    interview_id: str, user_id: Annotated[str, Depends(authorize)]
):
    interview_service = InterviewService(interview_id, user_id)
    chat_service = ChatService(interview_id, user_id)

    await interview_service.publish_interview_completed()
    await chat_service.end()

    return "Interview ended."


@router.get("/details/{interview_id}", responses={**NotFoundResponse})
async def get_interview_details(
    interview_id: str, user_id: Annotated[str, Depends(authorize)]
) -> InterviewDetailsResponse:
    messages = InterviewService(interview_id, user_id).get_conversation()
    if not messages:
        raise NotFoundException404("Interview not found.")

    conversation = [ConversationResponse.from_message(message) for message in messages]
    return InterviewDetailsResponse(
        interview_id=interview_id, conversations=conversation
    )


@router.get(
    "/report/{interview_id}", responses={**NotFoundResponse, **BadRequestResponse}
)
async def get_interview_report(
    interview_id: str, user_id: Annotated[str, Depends(authorize)]
) -> InterviewReportResponse:
    feedback_service = FeedbackService(interview_id)
    return feedback_service.get_feedback()
