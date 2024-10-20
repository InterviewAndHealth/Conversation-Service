import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends

from app import INTERVIEWS_SCHEDULE_RPC, USERS_RPC
from app.dependencies import authorize
from app.services.aws import AwsService
from app.services.broker import RPCService
from app.services.chat import ChatService
from app.services.chat_history import ChatHistoryService
from app.services.redis import RedisService
from app.types.communications import RPCPayloadType
from app.types.conversation_response import (
    ConversationResponse,
    InterviewDetailsResponse,
)
from app.types.message_request import MessageRequest
from app.types.message_response import MessageResponse
from app.utils.errors import (
    BadRequestException400,
    BadRequestResponse,
    NotFoundException404,
    NotFoundResponse,
)
from app.utils.pdf_text import fetch_pdf_text
from app.utils.timer import timer

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)

aws_service = AwsService()


@router.post("/start/{interview_id}", responses={**BadRequestResponse})
@timer
async def start_conversation(
    interview_id: str, user_id: Annotated[str, Depends(authorize)]
) -> MessageResponse:

    interview_details, resume_link = await asyncio.gather(
        RPCService.request(
            INTERVIEWS_SCHEDULE_RPC,
            RPCService.build_request_payload(
                RPCPayloadType.GET_INTERVIEW_DETAILS,
                {"interviewId": interview_id},
            ),
        ),
        RPCService.request(
            USERS_RPC,
            RPCService.build_request_payload(
                RPCPayloadType.GET_USER_RESUME,
                {"userId": user_id},
            ),
        ),
    )

    user_id_from_interview = interview_details.get("data").get("userid")
    if user_id != user_id_from_interview:
        raise BadRequestException400("User is not authorized for this interview.")

    job_description = interview_details.get("data").get("jobdescription")
    resume = await fetch_pdf_text(resume_link.get("data"))

    RedisService.set_job_description(interview_id, job_description)
    RedisService.set_resume(interview_id, resume)

    chat_service = ChatService(interview_id)

    if chat_service.is_active():
        raise BadRequestException400("Interview already started.")

    chat_service.set_active()
    return chat_service.start()


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
    chat_service = ChatService(interview_id)
    return chat_service.invoke(message.message)


@router.get("/details/{interview_id}", responses={**NotFoundResponse})
async def get_conversation(
    interview_id: str, user_id: Annotated[str, Depends(authorize)]
) -> InterviewDetailsResponse:

    messages = ChatHistoryService.get_messages(interview_id)

    if not messages or len(messages) == 0:
        raise NotFoundException404("Interview not found.")

    messages = messages[1:]  # Remove start message
    conversation = [ConversationResponse.from_message(message) for message in messages]

    return InterviewDetailsResponse(
        interview_id=interview_id, conversations=conversation
    )
