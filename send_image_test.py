"""Test script for sending messages with images via Telegram."""
import asyncio

from app.config import settings
from app.telegram import create_client, send_message


async def main():
    target = "your_target_or_chat_id"

    # Test 1: Send text only
    print("Test 1: Sending text only...")
    text = "测试消息（纯文本）"

    # Test 2: Send with image URL
    print("\nTest 2: Sending with image URL...")
    text_with_url = "测试消息（带图片URL）"
    image_url = "https://picsum.photos/400/300"  # Random placeholder image

    # Test 3: Send with local image path (if exists)
    print("\nTest 3: Sending with local image path...")
    text_with_path = "测试消息（带本地图片）"
    image_path = "/tmp/test_image.jpg"  # Update this path as needed

    client = create_client()
    await client.start()

    try:
        # Test 1
        result1 = await send_message(client, target, text)
        print(f"✓ Test 1 OK: message_id={result1['message_id']}")

        # Test 2
        result2 = await send_message(client, target, text_with_url, image_url=image_url)
        print(f"✓ Test 2 OK: message_id={result2['message_id']}")

        # Test 3 (only if file exists)
        import os
        if os.path.exists(image_path):
            result3 = await send_message(client, target, text_with_path, image_path=image_path)
            print(f"✓ Test 3 OK: message_id={result3['message_id']}")
        else:
            print(f"⊘ Test 3 SKIPPED: {image_path} not found")

    except ValueError as e:
        print(f"ERROR: {e}")
        print("Listing available dialogs:")
        async for dialog in client.iter_dialogs():
            print(f"  [{dialog.id}] {dialog.name}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
