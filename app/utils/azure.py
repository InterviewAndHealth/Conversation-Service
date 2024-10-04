import requests

from app import AZURE_KEY, AZURE_REGION, SPEECH_PROVIDER


class AzureTokenGenerator:
    def __init__(self):
        self.endpoint = (
            f"https://{AZURE_REGION}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        )
        self.headers = {
            "Ocp-Apim-Subscription-Key": AZURE_KEY,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def generate_token(self):
        if SPEECH_PROVIDER.lower() != "azure":
            return None
        try:
            response = requests.post(self.endpoint, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad responses
            return response.text
        except requests.exceptions.RequestException:
            return None
