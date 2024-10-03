from pydantic import BaseModel


class AwsResponse(BaseModel):
    url: str
    """The AWS URL to call."""
