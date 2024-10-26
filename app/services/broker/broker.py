import logging

import aio_pika

from app import EXCHANGE_NAME, RABBITMQ_URL


class Broker:
    """RabbitMQ broker"""

    _connection = None
    _channel = None
    _exchange = None

    @classmethod
    async def connect(cls):
        """Connect to RabbitMQ"""

        if cls._channel:
            return cls._channel
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            cls._connection = connection
            channel = await connection.channel()
            cls._channel = channel
            logging.info("Connected to RabbitMQ")
            return channel
        except Exception as err:
            logging.error(f"Failed to connect to RabbitMQ: {err}")

    @classmethod
    async def disconnect(cls):
        """Close the connection to RabbitMQ"""

        if cls._channel:
            await cls._exchange.delete()
            await cls._channel.close()
            await cls._connection.close()
            cls._channel = None
            logging.info("Closed RabbitMQ connection")

    @classmethod
    async def channel(cls):
        """Create a new channel"""

        if cls._exchange:
            return cls._exchange
        try:
            channel = await cls.connect()
            exchange = await channel.declare_exchange(
                EXCHANGE_NAME, aio_pika.ExchangeType.DIRECT, durable=True
            )
            cls._exchange = exchange
            logging.info("Created RabbitMQ exchange")
            return exchange
        except Exception as err:
            logging.error(f"Failed to create RabbitMQ channel: {err}")
