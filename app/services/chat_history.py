from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_redis import RedisChatMessageHistory

from app.services.redis import RedisService


class ChatHistoryService:
    """Service to interact with chat history."""

    @staticmethod
    def get_history(interview_id: str) -> RedisChatMessageHistory:
        """Get the chat history for the interview."""
        return RedisChatMessageHistory(
            interview_id,
            redis_client=RedisService.get_client(),
        )

    @staticmethod
    def add_message(interview_id: str, message: BaseMessage):
        """Add a message to the chat history."""
        ChatHistoryService.get_history(interview_id).add_message(message)

    @staticmethod
    def add_human_message(interview_id: str, message: str):
        """Add a human message to the chat history."""
        ChatHistoryService.get_history(interview_id).add_message(
            HumanMessage(content=message)
        )

    @staticmethod
    def add_system_message(interview_id: str, message: str):
        """Add a system message to the chat history."""
        ChatHistoryService.get_history(interview_id).add_message(
            SystemMessage(content=message)
        )

    @staticmethod
    def get_messages(interview_id: str):
        """Get messages in the chat history."""
        return [
            message
            for message in ChatHistoryService.get_history(interview_id).messages
            if isinstance(message, HumanMessage) or isinstance(message, AIMessage)
        ]

    @staticmethod
    def get_all_messages(interview_id: str):
        """Get all messages in the chat history."""
        return ChatHistoryService.get_history(interview_id).messages
