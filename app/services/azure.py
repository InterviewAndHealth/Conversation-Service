from fastapi import HTTPException

from app import AZURE_REGION, SPEECH_PROVIDER
from app.types.azure_response import AzureResponse
from app.utils.azure import AzureTokenGenerator


class AzureService:
    """Azure Service class"""

    def __init__(self):
        self.azure_token_generator = AzureTokenGenerator()

    def _validate_azure_service(self):
        """Validate Azure service."""
        if SPEECH_PROVIDER.lower() != "azure":
            raise HTTPException(status_code=400, detail="Azure service is not active.")

    def generate_token(self) -> AzureResponse:
        """Generate token."""
        self._validate_azure_service()
        token = self.azure_token_generator.generate_token()

        if not token:
            raise HTTPException(status_code=500, detail="Failed to generate token.")

        return AzureResponse(token=token, region=AZURE_REGION)
