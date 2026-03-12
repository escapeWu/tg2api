import asyncio
import sqlite3

import uvicorn

from app.api import app
from app.config import settings
from app.logging_config import get_logger, setup_logging
from app.pubsub import Publisher, load_subscribers
from app.telegram import create_client, register_handlers, verify_channels

setup_logging(settings.LOG_LEVEL)
logger = get_logger("main")

publisher = Publisher()
client = create_client()
register_handlers(client, publisher)


def _reset_update_state():
    """Clear saved update state so the client doesn't try to catch up on old messages."""
    db = f"{settings.TG_SESSION_NAME}.session"
    try:
        conn = sqlite3.connect(db)
        conn.execute("DELETE FROM update_state")
        conn.commit()
        conn.close()
        logger.info("Reset session update state")
    except Exception:
        logger.debug("No update state to reset")


async def _keep_connected(tg_client):
    """Keep the Telegram client connected, reconnecting on disconnect."""
    while True:
        try:
            await tg_client.run_until_disconnected()
        except Exception as e:
            logger.error(f"Telegram disconnected: {e}")
        logger.info("Telegram connection lost, reconnecting in 5s...")
        await asyncio.sleep(5)
        try:
            await tg_client.connect()
            logger.info("Telegram reconnected")
        except Exception as e:
            logger.error(f"Reconnect failed: {e}")


@app.on_event("startup")
async def startup_event():
    load_subscribers(publisher)
    _reset_update_state()
    await client.start()
    app.state.tg_client = client
    app.state.publisher = publisher
    await verify_channels(client)
    logger.info("Telegram listener started")
    asyncio.create_task(_keep_connected(client))


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
