from typing import Union

from redis import Redis
from redis.typing import ResponseT

from app import REDIS_URL


class RedisService:
    """Service to interact with Redis."""

    __client = Union[Redis, None]
    """Redis client instance."""

    class Namespace:
        """Namespace for Redis keys."""

        TIME = "time"
        """Namespace for time-related keys."""

        STATUS = "status"
        """Namespace for status-related keys."""

    class Status:
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
