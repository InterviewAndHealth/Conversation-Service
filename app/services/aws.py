from fastapi import HTTPException

from app import AWS_REGION, SPEECH_PROVIDER
from app.types.aws_response import AwsResponse
from app.utils.aws import AwsSignatureGenerator


class AwsService:
    """AWS Service class"""

    def __init__(self):
        self.aws_signature_generator = AwsSignatureGenerator()

    def is_active(self) -> bool:
        """Check if the AWS service is active."""
        return SPEECH_PROVIDER.lower() == "aws"

    def _validate_aws_service(self):
        """Validate AWS service."""
        if not self.is_active():
            raise HTTPException(status_code=400, detail="AWS service is not active.")

    def transcribe(self) -> AwsResponse:
        """Transcribe audio."""
        self._validate_aws_service()

        query = {
            "language-code": "en-US",
            "media-encoding": "pcm",
            "sample-rate": "44100",
        }

        url = self.aws_signature_generator.generate_presigned_url(
            method="GET",
            host=f"transcribestreaming.{AWS_REGION}.amazonaws.com:8443",
            path="/stream-transcription-websocket",
            service="transcribe",
            protocol="wss",
            expires=5 * 60,
            query=query,
        )

        return AwsResponse(url=url)

    def polly(self, text) -> AwsResponse:
        """Polly audio."""
        self._validate_aws_service()

        query = {
            "Engine": "neural",
            "LanguageCode": "en-US",
            "OutputFormat": "mp3",
            "SampleRate": "24000",
            "Text": text,
            "TextType": "text",
            "VoiceId": "Matthew",
        }

        url = self.aws_signature_generator.generate_presigned_url(
            method="GET",
            host=f"polly.{AWS_REGION}.amazonaws.com",
            path="/v1/speech",
            service="polly",
            protocol="https",
            expires=5 * 60,
            query=query,
        )

        return AwsResponse(url=url)
