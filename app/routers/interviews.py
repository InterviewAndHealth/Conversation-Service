from fastapi import APIRouter, Depends

from app.dependencies import authorize, authorize_interview
from app.fakedata import job_desc, resume
from app.services.aws import AwsService
from app.services.chat import ChatService
from app.services.chat_history import ChatHistoryService
from app.types.conversation_response import (
    ConversationResponse,
    InterviewDetailsResponse,
)
from app.types.message_request import MessageRequest
from app.types.message_response import MessageResponse
from app.utils.errors import (
    BadRequestException,
    BadRequestExceptionResponse,
    NotFoundException,
    NotFoundExceptionResponse,
)
from app.utils.timer import timer

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
    dependencies=[
        Depends(authorize),
        Depends(authorize_interview),
    ],
)

aws_service = AwsService()


@router.post("/start/{interview_id}", responses={**BadRequestExceptionResponse})
@timer
async def start_conversation(interview_id: str) -> MessageResponse:
    # TODO: Fetch job description and resume

    chat_service = ChatService(
        interview_id,
        job_description=job_desc,
        resume=resume,
    )

    if chat_service.is_active():
        raise BadRequestException("Interview already started.")

    chat_service.set_active()
    return chat_service.start()


@router.post(
    "/continue/{interview_id}",
    responses={**BadRequestExceptionResponse, **NotFoundExceptionResponse},
)
@timer
async def continue_conversation(
    interview_id: str, message: MessageRequest
) -> MessageResponse:
    chat_service = ChatService(interview_id)
    return chat_service.invoke(message.message)


@router.get("/details/{interview_id}", responses={**NotFoundExceptionResponse})
async def get_conversation(interview_id: str) -> InterviewDetailsResponse:
    messages = ChatHistoryService.get_messages(interview_id)

    if not messages or len(messages) == 0:
        raise NotFoundException("Interview not found.")

    messages = messages[1:]  # Remove start message
    conversation = [ConversationResponse.from_message(message) for message in messages]

    return InterviewDetailsResponse(
        interview_id=interview_id, conversations=conversation
    )
