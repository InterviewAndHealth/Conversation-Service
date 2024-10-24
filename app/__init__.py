import os

from dotenv import load_dotenv

load_dotenv(override=True)


# Server
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
ENV = os.getenv("ENV", "development")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Redis URL
REDIS_URL = os.getenv("REDIS_URL")

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Duration of the interview in minutes
INTERVIEW_DURATION = int(os.getenv("INTERVIEW_DURATION"))
FEEDBACK_DELAY = int(os.getenv("FEEDBACK_DELAY"), 10)

# Model
MODEL = os.getenv("MODEL")

# Groq settings
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Speech service provider
SPEECH_PROVIDER = os.getenv("SPEECH_PROVIDER")

# AWS
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_ROLE_ARN = os.getenv("AWS_ROLE_ARN")

# Azure
AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")

# RabbitMQ URL
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")

# RabbitMQ Service settings
SERVICE_NAME = os.getenv("SERVICE_NAME", "INTERVIEW_SERVICE")
SERVICE_QUEUE = os.getenv("SERVICE_QUEUE", "INTERVIEW_QUEUE")
RPC_QUEUE = os.getenv("RPC_QUEUE", "INTERVIEW_RPC")

USERS_QUEUE = os.getenv("USERS_QUEUE")
USERS_RPC = os.getenv("USERS_RPC")
INTERVIEWS_SCHEDULE_QUEUE = os.getenv("INTERVIEWS_SCHEDULE_QUEUE")
INTERVIEWS_SCHEDULE_RPC = os.getenv("INTERVIEWS_SCHEDULE_RPC")
SCHEDULER_QUEUE = os.getenv("SCHEDULER_QUEUE")


_imported_variable = {
    "HOST": HOST,
    "PORT": PORT,
    "DATABASE_URL": DATABASE_URL,
    "REDIS_URL": REDIS_URL,
    "JWT_SECRET_KEY": JWT_SECRET_KEY,
    "INTERVIEW_DURATION": INTERVIEW_DURATION,
    "SPEECH_PROVIDER": SPEECH_PROVIDER,
    "RABBITMQ_URL": RABBITMQ_URL,
    "EXCHANGE_NAME": EXCHANGE_NAME,
}

if USE_GROQ:
    _imported_variable.update({"GROQ_API_KEY": GROQ_API_KEY, "GROQ_MODEL": GROQ_MODEL})
else:
    _imported_variable.update({"MODEL": MODEL})

if SPEECH_PROVIDER and SPEECH_PROVIDER.lower() == "azure":
    _imported_variable.update({"AZURE_KEY": AZURE_KEY, "AZURE_REGION": AZURE_REGION})

if SPEECH_PROVIDER and SPEECH_PROVIDER.lower() == "aws":
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
