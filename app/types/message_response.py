from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str
    """The message."""


class MessageWithPollyResponse(MessageResponse):
    is_polly: bool = False
    """Whether the message has a Polly URL."""

    url: str = ""
    """The Polly URL."""
