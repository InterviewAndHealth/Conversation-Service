from pydantic import BaseModel


class MessageRequest(BaseModel):
    message: str
    """The message."""
