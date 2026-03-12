from abc import ABC, abstractmethod

from app.models import TGMessage


class Subscriber(ABC):
    """Base class for all message subscribers.

    Subclass this and implement `send()` to create a custom subscriber.
    Place your .py file in the `subscribers/` directory and it will be
    auto-discovered on startup.
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    async def send(self, message: TGMessage) -> None:
        """Process an incoming Telegram message."""
        ...
