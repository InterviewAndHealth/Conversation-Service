from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.utils import ConfigurableFieldSpec

from app import FEEDBACK_DELAY, INTERVIEW_DURATION, SCHEDULER_QUEUE, SERVICE_QUEUE
from app.services.broker.events import EventService
from app.services.chain import ChainService
from app.services.chat_history import ChatHistoryService
from app.services.redis import RedisService
from app.types.communications import EventType
from app.types.message_response import MessageResponse
from app.utils.errors import BadRequestException400, NotFoundException404


class ChatService:
    """Service for handling conversation chat."""

    _INPUT_MESSAGES_KEY = "input"
    _HISTORY_MESSAGES_KEY = "history"
    _INTERVIEW_ID_KEY = "interview_id"

    def __init__(
        self,
        interview_id: str,
        user_id: str,
    ):
        self.interview_id = interview_id

        if user_id != RedisService.get_user(self.interview_id):
            raise BadRequestException400("User not authorized.")

        self.job_description = RedisService.get_job_description(self.interview_id)
        self.resume = RedisService.get_resume(self.interview_id)

        if not self.job_description or not self.resume:
            raise NotFoundException404("Interview not found.")

        self.chain = ChainService(
            job_description=self.job_description,
            resume=self.resume,
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
            raise BadRequestException400("Inactive interview.")

        response = self.runnable.invoke(
            {self._INPUT_MESSAGES_KEY: message},
            config={"configurable": {self._INTERVIEW_ID_KEY: self.interview_id}},
        )

        return MessageResponse(message=response.content)

    async def start(self) -> MessageResponse:
        """Start the chat service."""
        RedisService.set_job_description(self.interview_id, self.job_description)
        RedisService.set_resume(self.interview_id, self.resume)

        await EventService.publish(
            SCHEDULER_QUEUE,
            EventService.build_request_payload(
                type=EventType.SCHEDULE_EVENT,
                data={
                    "id": self.interview_id,
                    "seconds": (INTERVIEW_DURATION + FEEDBACK_DELAY) * 60,
                    "service": SERVICE_QUEUE,
                    "type": EventType.GENERATE_REPORT,
                    "data": {"interview_id": self.interview_id},
                },
            ),
        )

        return self.invoke("Hello")

    async def end(self) -> None:
        """End the chat service."""
        self.set_inactive()

        await EventService.publish(
            SCHEDULER_QUEUE,
            EventService.build_request_payload(
                type=EventType.SCHEDULE_EVENT,
                data={
                    "id": self.interview_id,
                    "seconds": FEEDBACK_DELAY * 60,
                    "service": SERVICE_QUEUE,
                    "type": EventType.GENERATE_REPORT,
                    "data": {"interview_id": self.interview_id},
                },
            ),
        )
