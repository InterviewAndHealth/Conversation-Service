from pydantic import BaseModel


class AzureResponse(BaseModel):
    token: str
    """The Azure token."""

    region: str
    """The Azure region."""
