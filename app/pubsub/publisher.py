from app.logging_config import get_logger
from app.models import TGMessage
from app.pubsub.subscriber import Subscriber

logger = get_logger("publisher")


class Publisher:
    def __init__(self) -> None:
        self._subscribers: list[Subscriber] = []

    def register(self, subscriber: Subscriber) -> None:
        self._subscribers.append(subscriber)
        logger.info(f"Registered subscriber: {subscriber.name}")

    async def publish(self, message: TGMessage) -> None:
        for sub in self._subscribers:
            try:
                await sub.send(message)
            except Exception:
                logger.exception(f"Subscriber {sub.name} failed to process message {message.message_id}")
