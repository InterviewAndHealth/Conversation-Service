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
            exchange = await Broker.channel()
            message = json.dumps(data)
            await exchange.publish(
                aio_pika.Message(body=message.encode()), routing_key=service
            )
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
            # Connect to RabbitMQ and declare queue
            channel = await Broker.connect()
            queue = await channel.declare_queue(
                SERVICE_QUEUE, durable=True, arguments={"x-queue-type": "quorum"}
            )
            await queue.bind(exchange=EXCHANGE_NAME, routing_key=service)

            async def process_message(message: aio_pika.IncomingMessage):
                async with message.process(ignore_processed=True):  # Prevent auto ack
                    try:
                        data = json.loads(message.body)
                        await subscriber.handle_event(data)  # Call subscriber method
                        await message.ack()  # Acknowledge on success
                    except Exception as process_error:
                        logging.error(f"Error processing message: {process_error}")
                        await message.nack(requeue=True)  # Requeue on failure

            # Consume messages
            await queue.consume(process_message)
            logging.info(f"Subscribed to service: {service}")
        except Exception as err:
            logging.error(f"Subscription error for {service}: {err}")
