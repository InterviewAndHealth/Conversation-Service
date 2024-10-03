from fastapi import HTTPException
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.utils import ConfigurableFieldSpec

from app.services.chain import ChainService
from app.services.chat_history import ChatHistoryService
from app.services.redis import RedisService
from app.types.message_response import MessageResponse


class ChatService:
    """Service for handling conversation chat."""

    _INPUT_MESSAGES_KEY = "input"
    _HISTORY_MESSAGES_KEY = "history"
    _INTERVIEW_ID_KEY = "interview_id"

    def __init__(
        self,
        interview_id: str,
        job_description: str = None,
        resume: str = None,
    ):
        self.interview_id = interview_id

        self.chain = ChainService(
            job_description=job_description,
            resume=resume,
        ).get_chain()

        self.runnable = RunnableWithMessageHistory(
            self.chain,
            ChatHistoryService.get_history,
            input_messages_key=self._INPUT_MESSAGES_KEY,
            history_messages_key=self._HISTORY_MESSAGES_KEY,
            history_factory_config=[
                ConfigurableFieldSpec(
                    id=self._INTERVIEW_ID_KEY,
                    annotation=str,
                    name="Interview ID",
                    description="The interview ID.",
                    is_shared=True,
                )
            ],
        )

    def set_active(self):
        """Set the chat service to active."""
        RedisService.set_status(self.interview_id, RedisService.Status.ACTIVE)

    def set_inactive(self):
        """Set the chat service to inactive."""
        RedisService.set_status(self.interview_id, RedisService.Status.INACTIVE)

    def is_active(self) -> bool:
        """Check if the chat service is active."""
        return RedisService.get_status(self.interview_id) == RedisService.Status.ACTIVE

    def invoke(self, message: str) -> MessageResponse:
        """Invoke the chat service with a message."""
        if not self.is_active():
            raise HTTPException(
                status_code=400,
                detail="Inactive interview.",
            )

        response = self.runnable.invoke(
            {self._INPUT_MESSAGES_KEY: message},
            config={"configurable": {self._INTERVIEW_ID_KEY: self.interview_id}},
        )

        return MessageResponse(message=response.content)

    def start(self) -> MessageResponse:
        """Start the chat service."""
        return self.invoke("Hello")
