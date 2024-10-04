import asyncio
import json
import logging
import uuid

import aio_pika

from app import RPC_QUEUE
from app.services.broker import Broker
from app.utils.errors import RequestTimeoutException


class RPCService:
    """RPC service"""

    @staticmethod
    async def request(
        service_rpc: str,
        request_payload: dict,
        timeout: int = 10,
    ) -> dict:
        """
        Request data from a service

        Parameters
        ----------
        service_rpc : str
            The service to request data from
        request_payload : dict
            The request payload
        timeout : int, optional
            The request timeout, by default 10

        Returns
        -------
        dict
            The response data

        Examples
        --------
        >>> RPCService.request("service", {"key": "value"})
        """

        try:
            correlation_id = str(uuid.uuid4())
            channel = await Broker.connect()
            queue = await channel.declare_queue("", exclusive=True)

            future = asyncio.get_event_loop().create_future()

            async def on_response(message: aio_pika.IncomingMessage):
                if message.correlation_id == correlation_id:
                    if not future.done():
                        future.set_result(json.loads(message.body))
                        await message.ack()

            await queue.consume(on_response)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(request_payload).encode(),
                    correlation_id=correlation_id,
                    reply_to=queue.name,
                ),
                routing_key=service_rpc,
            )

            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            raise RequestTimeoutException()
        except Exception as err:
            logging.error(f"Failed to request data: {err}")

    @staticmethod
    async def respond(responder):
        """
        Respond to RPC requests

        Parameters
        ----------
        responder : object
            The service responder with a respond_rpc method

        Returns
        -------
        None

        Examples
        --------
        >>> class Responder:
        ...     @staticmethod
        ...     def respond_rpc(self, message):
        ...         return message
        ...
        >>> RPCService.respond(Responder)
        """

        try:
            channel = await Broker.connect()
            queue = await channel.declare_queue(RPC_QUEUE)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        request_payload = json.loads(message.body)
                        response = await responder.respond_rpc(request_payload)
                        await channel.default_exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(response).encode(),
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to,
                        )
        except Exception as err:
            logging.error(f"Failed to respond to request: {err}")
