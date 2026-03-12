from urllib.parse import urlparse

import socks
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel

from app.config import settings
from app.logging_config import get_logger
from app.models import TGMessage
from app.pubsub.publisher import Publisher

logger = get_logger("telegram")

PROXY_SCHEMES = {"socks5": socks.SOCKS5, "socks4": socks.SOCKS4, "http": socks.HTTP}


def _parse_proxy(url: str) -> tuple:
    p = urlparse(url)
    return (PROXY_SCHEMES[p.scheme], p.hostname, p.port)


def create_client() -> TelegramClient:
    kwargs = {}
    if settings.TG_PROXY:
        kwargs["proxy"] = _parse_proxy(settings.TG_PROXY)
    return TelegramClient(
        settings.TG_SESSION_NAME,
        settings.TG_API_ID,
        settings.TG_API_HASH,
        **kwargs,
    )


async def verify_channels(client: TelegramClient) -> None:
    """Log whether each configured channel is accessible."""
    for ch in settings.CHANNELS_TO_WATCH:
        try:
            entity = await client.get_entity(ch)
            logger.info(f"Channel OK: @{ch} -> {entity.title} (id={entity.id})")
        except Exception as e:
            logger.error(f"Channel FAILED: @{ch} -> {e}")


async def find_entity_by_title(client: TelegramClient, title: str):
    """Iterate dialogs to find a chat whose display name matches title."""
    async for dialog in client.iter_dialogs():
        if dialog.name == title:
            return dialog.entity
    return None


def _parse_target_as_peer(target: str):
    value = target.strip()
    if not value:
        return None
    if value.startswith("-100") and value[4:].isdigit():
        return PeerChannel(int(value[4:]))
    if value.startswith("@"):
        return value
    if value.lstrip("-").isdigit():
        return int(value)
    return value


async def send_message(
    client: TelegramClient,
    target: str,
    text: str,
    image_url: str | None = None,
    image_path: str | None = None
) -> dict:
    """Send a message to a chat by username, display name, or chat ID.

    target can be:
    - A Telegram username, e.g. "somegroup" or "@somegroup"
    - The display name (title) of any dialog in the account's chat list
    - A chat ID, e.g. "-1003883242492"

    Supports sending images via:
    - image_url: URL of image to download and send
    - image_path: Local file path of image to send
    """
    entity = None
    if not client.is_connected():
        logger.warning("Telegram client disconnected, reconnecting before send...")
        await client.connect()

    parsed_target = _parse_target_as_peer(target)
    try:
        entity = await client.get_entity(parsed_target)
    except Exception as e:
        logger.debug("get_entity failed for target=%r parsed=%r: %s", target, parsed_target, e)

    if entity is None and isinstance(parsed_target, str):
        entity = await find_entity_by_title(client, parsed_target)

    if entity is None:
        raise ValueError(f"Chat not found: {target!r}")

    # Determine which file to send
    file_to_send = None
    if image_url:
        file_to_send = image_url
    elif image_path:
        file_to_send = image_path

    # Send message with or without image
    if file_to_send:
        msg = await client.send_message(entity, text, file=file_to_send)
    else:
        msg = await client.send_message(entity, text)

    return {"message_id": msg.id, "target": target}


def register_handlers(client: TelegramClient, publisher: Publisher) -> None:
    @client.on(events.NewMessage(chats=settings.CHANNELS_TO_WATCH))
    async def on_new_message(event: events.NewMessage.Event) -> None:
        channel = event.chat.username or str(event.chat.id)
        message = TGMessage(
            channel=channel,
            message_id=event.message.id,
            text=event.message.message or "",
            date=event.message.date.isoformat(),
            media=event.message.media is not None,
        )
        logger.info(f"New message from @{channel} (ID: {message.message_id})")
        await publisher.publish(message)
