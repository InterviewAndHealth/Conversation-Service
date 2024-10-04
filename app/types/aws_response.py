from pydantic import BaseModel


class AwsResponse(BaseModel):
    accessKeyId: str
    """The AWS access key ID."""

    secretAccessKey: str
    """The AWS secret access key."""

    sessionToken: str
    """The AWS security or session token."""

    region: str
    """The AWS region."""
