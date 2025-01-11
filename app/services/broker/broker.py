import logging

import aio_pika

from app import RABBITMQ_URL


class Broker:
    """RabbitMQ broker"""

    _connection = None

    @classmethod
    async def connect(cls) -> aio_pika.Connection:
        """Connect to RabbitMQ"""

        try:
            if cls._connection:
                return cls._connection
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            cls._connection = connection
            logging.info("Connected to RabbitMQ")
            return connection
        except Exception as err:
            logging.error(f"Failed to connect to RabbitMQ: {err}")

    @classmethod
    async def close(cls):
        """Close the connection to RabbitMQ"""

        if cls._connection:
            await cls._connection.close()
            cls._connection = None
            logging.info("Closed RabbitMQ connection")
