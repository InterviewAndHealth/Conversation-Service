import boto3

from app import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_ROLE_ARN,
    AWS_SECRET_ACCESS_KEY,
    SPEECH_PROVIDER,
)


class AwsCredentialsGenerator:
    def __init__(self):
        if SPEECH_PROVIDER.lower() == "aws":
            self.sts_client = boto3.client(
                "sts",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION,
            )

    def generate_credentials(self, interview_id: str = ""):
        if SPEECH_PROVIDER.lower() != "aws":
            return None
        try:
            assumed_role = self.sts_client.assume_role(
                RoleArn=AWS_ROLE_ARN,
                RoleSessionName=interview_id,
                DurationSeconds=30 * 60,
            )
            return assumed_role.get("Credentials")
        except Exception as e:
            return None
