from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class ConversationResponse(BaseModel):
    type: str
    """The type of the message."""

    message: str
    """The message."""

    @classmethod
    def from_message(cls, message: BaseMessage) -> "ConversationResponse":
        return cls(message=message.content, type=message.type)
