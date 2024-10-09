from app import AWS_REGION, SPEECH_PROVIDER
from app.types.aws_response import AwsResponse
from app.utils.aws import AwsCredentialsGenerator
from app.utils.errors import BadRequestException400, InternalServerErrorException500


class AwsService:
    """AWS Service class"""

    def __init__(self):
        self.aws_credentials_generator = AwsCredentialsGenerator()

    def _validate_aws_service(self):
        """Validate AWS service."""
        if SPEECH_PROVIDER.lower() != "aws":
            raise BadRequestException400("AWS service is not active.")

    def generate_credentials(self, interview_id: str = "") -> AwsResponse:
        """Generate credentials."""
        self._validate_aws_service()
        credentials = self.aws_credentials_generator.generate_credentials(interview_id)

        if not credentials:
            raise InternalServerErrorException500("Failed to generate credentials.")

        return AwsResponse(
            accessKeyId=credentials.get("AccessKeyId"),
            secretAccessKey=credentials.get("SecretAccessKey"),
            sessionToken=credentials.get("SessionToken"),
            region=AWS_REGION,
        )
