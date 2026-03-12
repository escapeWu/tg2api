"""NewsRaterSubscriber

Buffers incoming Telegram messages and sends them in a single batch to the
news-rater agent API after a configurable debounce window.

Debounce logic:
  - Each new message resets a 5-second countdown timer.
  - When the timer fires (no new message for 5 s), all buffered messages are
    joined with " --- " and posted to the news-rater endpoint in one request.
"""

import asyncio
import os
from typing import Optional

import httpx

from app.logging_config import get_logger
from app.models import TGMessage
from app.pubsub.subscriber import Subscriber

logger = get_logger("news_rater")

_NEWS_RATER_URLS = (
    os.getenv("NEWS_RATER_URL", "http://localhost:3099/api/agents/news-rater/run"),
)
_DEBOUNCE_SECONDS = 5.0


class NewsRaterSubscriber(Subscriber):

    def __init__(self) -> None:
        self._buffer: list[TGMessage] = []
        self._timer_task: Optional[asyncio.Task] = None

    async def send(self, message: TGMessage) -> None:
        self._buffer.append(message)
        logger.debug(
            "Buffered msg %s from %s (buffer=%d)",
            message.message_id,
            message.channel,
            len(self._buffer),
        )

        # Cancel existing countdown and restart it.
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()

        self._timer_task = asyncio.create_task(self._flush_after_delay())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _flush_after_delay(self) -> None:
        try:
            await asyncio.sleep(_DEBOUNCE_SECONDS)
            await self._flush()
        except asyncio.CancelledError:
            pass  # A newer message reset the timer; nothing to do.

    async def _flush(self) -> None:
        if not self._buffer:
            return

        messages = self._buffer[:]
        self._buffer.clear()

        news_input = "\n---\n".join(self._format_message(m) for m in messages)

        payload = {
            "params": {
                "news_input": news_input,
                "relation": "",  # empty → auto-detected by the agent
            }
        }

        logger.info("Sending %d buffered message(s) to news-rater", len(messages))

        async with httpx.AsyncClient() as client:
            for url in _NEWS_RATER_URLS:
                try:
                    resp = await client.post(
                        url,
                        json=payload,
                        timeout=30.0,
                    )
                    if resp.status_code == 200:
                        task_id = resp.json().get("task_id", "?")
                        logger.info(
                            "news-rater accepted %d message(s), task_id=%s, url=%s",
                            len(messages),
                            task_id,
                            url,
                        )
                    else:
                        logger.error(
                            "news-rater returned %d: %s, url=%s",
                            resp.status_code,
                            resp.text[:300],
                            url,
                        )
                except Exception:
                    logger.exception(
                        "Failed to send %d message(s) to news-rater, url=%s",
                        len(messages),
                        url,
                    )

    @staticmethod
    def _format_message(msg: TGMessage) -> str:
        lines = msg.text.strip().splitlines()
        title = lines[0] if lines else ""
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""
        parts = [title]
        if body:
            parts.append(body)
        parts.append(f"来源: {msg.channel}")
        parts.append(f"时间: {msg.date}")
        return "\n".join(parts)
