import os

from dotenv import load_dotenv

load_dotenv(override=True)


# Server
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
ENV = os.getenv("ENV", "development")

# Redis URL
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

REDIS_URL = os.getenv(
    "REDIS_URL",
    f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0",
)

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Duration of the interview in minutes
INTERVIEW_DURATION = os.getenv("INTERVIEW_DURATION")
FEEDBACK_DELAY = int(os.getenv("FEEDBACK_DELAY", 5))

# Model
MODEL = os.getenv("MODEL") or os.getenv("CONVERSATION_SERVICE_MODEL")

# Groq settings
USE_GROQ = (
    os.getenv("USE_GROQ") or os.getenv("CONVERSATION_SERVICE_USE_GROQ") or "false"
).lower() == "true"
GROQ_MODEL = os.getenv("GROQ_MODEL") or os.getenv("CONVERSATION_SERVICE_GROQ_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv(
    "CONVERSATION_SERVICE_GROQ_API_KEY"
)

# Speech service provider
SPEECH_PROVIDERS = os.getenv("SPEECH_PROVIDERS")

# AWS
AWS_REGION = os.getenv("AWS_REGION") or os.getenv("CONVERSATION_SERVICE_AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv(
    "CONVERSATION_SERVICE_AWS_ACCESS_KEY_ID"
)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv(
    "CONVERSATION_SERVICE_AWS_SECRET_ACCESS_KEY"
)
AWS_ROLE_ARN = os.getenv("AWS_ROLE_ARN") or os.getenv(
    "CONVERSATION_SERVICE_AWS_ROLE_ARN"
)

# Azure
AZURE_KEY = os.getenv("AZURE_KEY") or os.getenv("CONVERSATION_SERVICE_AZURE_KEY")
AZURE_REGION = os.getenv("AZURE_REGION") or os.getenv(
    "CONVERSATION_SERVICE_AZURE_REGION"
)

# RabbitMQ URL
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    f"amqp://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}",
)
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")

# RabbitMQ Service settings
SERVICE_NAME = os.getenv("SERVICE_NAME", "CONVERSATION_SERVICE")
SERVICE_QUEUE = os.getenv("CONVERSATION_QUEUE", "CONVERSATION_QUEUE")
RPC_QUEUE = os.getenv("CONVERSATION_RPC", "CONVERSATION_RPC")

USERS_QUEUE = os.getenv("USER_QUEUE")
USERS_RPC = os.getenv("USER_RPC")
INTERVIEWS_QUEUE = os.getenv("INTERVIEW_QUEUE")
INTERVIEWS_RPC = os.getenv("INTERVIEW_RPC")
SCHEDULER_QUEUE = os.getenv("SCHEDULER_QUEUE")


_imported_variable = {
    "HOST": HOST,
    "PORT": PORT,
    "REDIS_URL": REDIS_URL,
    "JWT_SECRET_KEY": JWT_SECRET_KEY,
    "INTERVIEW_DURATION": INTERVIEW_DURATION,
    "SPEECH_PROVIDERS": SPEECH_PROVIDERS,
    "RABBITMQ_URL": RABBITMQ_URL,
    "EXCHANGE_NAME": EXCHANGE_NAME,
}

if USE_GROQ:
    _imported_variable.update({"GROQ_API_KEY": GROQ_API_KEY, "GROQ_MODEL": GROQ_MODEL})
else:
    _imported_variable.update({"MODEL": MODEL})

if SPEECH_PROVIDERS and "azure" in SPEECH_PROVIDERS.lower():
    _imported_variable.update({"AZURE_KEY": AZURE_KEY, "AZURE_REGION": AZURE_REGION})

if SPEECH_PROVIDERS and "aws" in SPEECH_PROVIDERS.lower():
    _imported_variable.update(
        {
            "AWS_REGION": AWS_REGION,
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "AWS_ROLE_ARN": AWS_ROLE_ARN,
        }
    )

if not all(_imported_variable.values()):
    missing_variables = [key for key, value in _imported_variable.items() if not value]
    raise ValueError(f"Missing environment variables: {missing_variables}")

INTERVIEW_DURATION = int(INTERVIEW_DURATION)
SPEECH_PROVIDERS = [
    provider.strip().lower() for provider in SPEECH_PROVIDERS.split(",")
]
