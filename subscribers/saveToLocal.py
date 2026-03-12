import csv
import os
from pathlib import Path

from app.logging_config import get_logger
from app.models import TGMessage
from app.pubsub.subscriber import Subscriber

logger = get_logger("save_to_local")

CSV_PATH = Path("data/messages.csv")


class SaveToLocalSubscriber(Subscriber):
    """Saves incoming messages to a local CSV file.

    Appends each message as a row with columns: channelName, content, time.
    The CSV file and data/ directory are created automatically on first write.
    """

    FIELDNAMES = ["channelName", "content", "time"]

    async def send(self, message: TGMessage) -> None:
        try:
            file_exists = CSV_PATH.exists()

            CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                if not file_exists:
                    writer.writeheader()
                writer.writerow({
                    "channelName": message.channel,
                    "content": message.text,
                    "time": message.date,
                })

            logger.info(f"Saved message from @{message.channel} to {CSV_PATH}")
        except Exception:
            logger.exception(f"Failed to save message to {CSV_PATH}")
