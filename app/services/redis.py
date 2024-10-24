from enum import StrEnum
from typing import Union

from redis import Redis
from redis.commands.json.path import Path
from redis.typing import ResponseT

from app import REDIS_URL


class RedisService:
    """Service to interact with Redis."""

    __client = Union[Redis, None]
    """Redis client instance."""

    class Namespace(StrEnum):
        """Namespace for Redis keys."""

        TIME = "time"
        """Namespace for time-related keys."""

        STATUS = "status"
        """Namespace for status-related keys."""

        USER = "user"
        """Namespace for user-related keys."""

        JOB_DESCRIPTION = "job_description"
        """Namespace for job description-related keys."""

        RESUME = "resume"
        """Namespace for resume-related keys."""

        FEEDBACK = "feedback"
        """Namespace for feedback-related keys."""

    class Status(StrEnum):
        """Status values for Redis keys."""

        ACTIVE = "active"
        """Active status."""

        INACTIVE = "inactive"
        """Inactive status."""

    @staticmethod
    def connect():
        """Connect to Redis."""
        RedisService.__client = Redis.from_url(REDIS_URL)

    @staticmethod
    def disconnect():
        """Disconnect from Redis."""
        if RedisService.__client is not None:
            RedisService.__client.close()
            RedisService.__client = None

    @staticmethod
    def get_client() -> Redis:
        """Get Redis client."""
        if RedisService.__client is None:
            RedisService.connect()

        return RedisService.__client

    @staticmethod
    def get(key) -> ResponseT:
        """Get a value from Redis."""
        return RedisService.get_client().get(key)

    @staticmethod
    def set(key, value) -> None:
        """Set a value in Redis."""
        RedisService.get_client().set(key, value)

    @staticmethod
    def setKeyWithNamespace(namespace, key, value) -> None:
        """Set a value in Redis with a namespace."""
        RedisService.get_client().set(f"{namespace}:{key}", value)

    @staticmethod
    def getKeyWithNamespace(namespace, key) -> ResponseT:
        """Get a value from Redis with a namespace."""
        return RedisService.get_client().get(f"{namespace}:{key}")

    @staticmethod
    def set_time(key, value) -> None:
        """Set a time-related value in Redis."""
        RedisService.setKeyWithNamespace(RedisService.Namespace.TIME, key, value)

    @staticmethod
    def get_time(key) -> ResponseT:
        """Get a time-related value from Redis."""
        return RedisService.getKeyWithNamespace(RedisService.Namespace.TIME, key)

    @staticmethod
    def set_status(key, value) -> None:
        """Set a status-related value in Redis."""
        RedisService.setKeyWithNamespace(RedisService.Namespace.STATUS, key, value)

    @staticmethod
    def get_status(key) -> Union[str, None]:
        """Get a status-related value from Redis."""
        raw = RedisService.getKeyWithNamespace(RedisService.Namespace.STATUS, key)
        return raw.decode("utf-8") if raw else None

    @staticmethod
    def set_user(key, value) -> None:
        """Set a user-related value in Redis."""
        RedisService.setKeyWithNamespace(RedisService.Namespace.USER, key, value)

    @staticmethod
    def get_user(key) -> ResponseT:
        """Get a user-related value from Redis."""
        raw = RedisService.getKeyWithNamespace(RedisService.Namespace.USER, key)
        return raw.decode("utf-8") if raw else None

    @staticmethod
    def set_job_description(key, value) -> None:
        """Set a job description-related value in Redis."""
        RedisService.setKeyWithNamespace(
            RedisService.Namespace.JOB_DESCRIPTION, key, value
        )

    @staticmethod
    def get_job_description(key) -> ResponseT:
        """Get a job description-related value from Redis."""
        raw = RedisService.getKeyWithNamespace(
            RedisService.Namespace.JOB_DESCRIPTION, key
        )
        return raw.decode("utf-8") if raw else None

    @staticmethod
    def set_resume(key, value) -> None:
        """Set a resume-related value in Redis."""
        RedisService.setKeyWithNamespace(RedisService.Namespace.RESUME, key, value)

    @staticmethod
    def get_resume(key) -> ResponseT:
        """Get a resume-related value from Redis."""
        raw = RedisService.getKeyWithNamespace(RedisService.Namespace.RESUME, key)
        return raw.decode("utf-8") if raw else None

    @staticmethod
    def set_feedback(key, value: dict) -> None:
        """Set a feedback-related value in Redis."""
        RedisService.get_client().json().set(
            f"{RedisService.Namespace.FEEDBACK}:{key}", Path.root_path(), value
        )

    @staticmethod
    def get_feedback(key) -> dict:
        """Get a feedback-related value from Redis."""
        return (
            RedisService.get_client()
            .json()
            .get(f"{RedisService.Namespace.FEEDBACK}:{key}")
        )
