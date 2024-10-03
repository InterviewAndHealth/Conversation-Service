from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import authorize, authorize_interview

# TODO: Remove this import
from app.fakedata import job_desc, resume
from app.services.aws import AwsService
from app.services.chat import ChatService
from app.services.chat_history import ChatHistoryService
from app.types.conversation_response import ConversationResponse
from app.types.message_request import MessageRequest
from app.types.message_response import MessageWithPollyResponse
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


@router.post("/{interview_id}/start")
@timer
async def start_conversation(interview_id: str) -> MessageWithPollyResponse:
    # TODO: Fetch job description and resume

    chat = ChatService(
        interview_id,
        job_description=job_desc,
        resume=resume,
    )

    if chat.is_active():
        raise HTTPException(
            status_code=400,
            detail="Interview already started.",
        )

    chat.set_active()
    message = chat.start().message
    polly = aws_service.polly(message).url if aws_service.is_active() else None

    return MessageWithPollyResponse(
        message=message,
        is_polly=polly is not None,
        url=polly,
    )


@router.post("/{interview_id}/chat")
@timer
async def continue_conversation(
    interview_id: str, message: MessageRequest
) -> MessageWithPollyResponse:
    chat = ChatService(
        interview_id,
        job_description=job_desc,
        resume=resume,
    )

    if not chat.is_active():
        raise HTTPException(
            status_code=400,
            detail="Inactive interview.",
        )

    message = chat.invoke(message.message).message
    polly = aws_service.polly(message).url if aws_service.is_active() else None
    return MessageWithPollyResponse(
        message=message,
        is_polly=polly is not None,
        url=polly,
    )


@router.get("/{interview_id}")
async def get_conversation(interview_id: str) -> list[ConversationResponse]:
    messages = ChatHistoryService.get_messages(interview_id)
    if not messages or len(messages) == 0:
        raise HTTPException(
            status_code=404,
            detail="No messages found.",
        )
    messages = messages[1:]  # Remove start message
    conversation = [ConversationResponse.from_message(message) for message in messages]
    return conversation
