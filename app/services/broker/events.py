import json
import logging

import aio_pika

from app import EXCHANGE_NAME, SERVICE_QUEUE
from app.services.broker import Broker


class EventService:
    """Publish and subscribe to events"""

    @staticmethod
    def build_request_payload(
        type: str,
        data: dict,
    ) -> dict:
        """
        Build a request payload

        Parameters
        ----------
        type : str
            The request type
        data : dict
            The request data

        Returns
        -------
        dict
            The request payload

        Examples
        --------
        >>> RPCService.build_request_payload("type", {"key": "value"})
        """

        return {
            "type": type,
            "data": data,
        }

    _publishChannel = None

    @staticmethod
    async def _get_publish_channel():
        """Return a channel and exchange for publishing events"""
        if EventService._publishChannel:
            return EventService._publishChannel

        connection = await Broker.connect()
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        EventService._publishChannel = exchange
        return exchange

    @staticmethod
    async def publish(service: str, data: dict):
        """
        Publish an event to a service

        Parameters
        ----------
        service : str
            The service to publish the event to
        data : dict
            The event data

        Returns
        -------
        None

        Examples
        --------
        >>> await EventService.publish("service", {"key": "value"})
        """
        try:
            exchange = await EventService._get_publish_channel()
            message = json.dumps(data)
            await exchange.publish(
                aio_pika.Message(body=message.encode()), routing_key=service
            )
            logging.info(f"Published event to {service}")
        except Exception as err:
            logging.error(f"Failed to publish event: {err}")

    @staticmethod
    async def subscribe(service: str, subscriber):
        """
        Subscribe to events from a service

        Parameters
        ----------
        service : str
            The service to subscribe to
        subscriber : class or object
            The service subscriber with a handle_event method

        Returns
        -------
        None

        Examples
        --------
        >>> class Subscriber:
        ...     @staticmethod
        ...     async def handle_event(message):
        ...         print(message)
        ...
        >>> await EventService.subscribe("service", Subscriber)
        """
        try:
            connection = await Broker.connect()
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            exchange = await channel.declare_exchange(
                EXCHANGE_NAME,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
            queue = await channel.declare_queue(
                SERVICE_QUEUE,
                durable=True,
                arguments={"x-queue-type": "quorum"},
            )
            await queue.bind(exchange=exchange, routing_key=service)

            async def process_message(message: aio_pika.IncomingMessage):
                async with message.process(ignore_processed=True):
                    try:
                        data = json.loads(message.body)
                        await subscriber.handle_event(data)
                        await message.ack()
                    except Exception as process_error:
                        logging.error(f"Error processing message: {process_error}")
                        await message.nack(requeue=True)

            await queue.consume(process_message, no_ack=False)
            logging.info(f"Subscribed to service: {service}")
        except Exception as err:
            logging.error(f"Subscription error for {service}: {err}")
