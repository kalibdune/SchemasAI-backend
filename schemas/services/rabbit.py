import asyncio
import json
import uuid
from typing import MutableMapping

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractQueue,
)

from schemas.config import config
from schemas.db.schemas.message import MessageSchema


class RabbitClientService:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue

    def __init__(self, url: str = config.rabbit.get_url) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.url = url

    async def connect(self) -> "RabbitClientService":
        self.connection = await connect(self.url)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self._on_response, no_ack=True)
        return self

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, routing_key: str, message: MessageSchema) -> MessageSchema:
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                message.model_dump_json().encode(),
                content_type="application/json",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=routing_key,
        )

        return MessageSchema.model_validate(json.loads((await future).decode()))
