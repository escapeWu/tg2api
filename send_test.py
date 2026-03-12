"""Standalone script to send a single Telegram message using the existing session."""
import asyncio

from app.config import settings
from app.telegram import create_client, send_message


async def main():
    target = "your_target_or_chat_id"
    text = "这是一条机器人发送的消息，TESTING"

    client = create_client()
    await client.start()
    try:
        result = await send_message(client, target, text)
        print(f"OK: message_id={result['message_id']}, target={result['target']!r}")
    except ValueError as e:
        print(f"ERROR: {e}")
        print("Listing available dialogs to help find the correct name:")
        async for dialog in client.iter_dialogs():
            print(f"  [{dialog.id}] {dialog.name}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
