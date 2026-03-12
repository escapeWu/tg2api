import importlib
import inspect
import os
import sys

from app.logging_config import get_logger
from app.pubsub.publisher import Publisher
from app.pubsub.subscriber import Subscriber

logger = get_logger("loader")

SUBSCRIBERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "subscribers")


def load_subscribers(publisher: Publisher) -> None:
    """Scan subscribers/ directory and register all Subscriber subclasses."""
    if not os.path.isdir(SUBSCRIBERS_DIR):
        logger.warning(f"Subscribers directory not found: {SUBSCRIBERS_DIR}")
        return

    # Ensure subscribers dir is importable
    if SUBSCRIBERS_DIR not in sys.path:
        sys.path.insert(0, os.path.dirname(SUBSCRIBERS_DIR))

    found = 0
    for filename in sorted(os.listdir(SUBSCRIBERS_DIR)):
        if not filename.endswith(".py") or filename.startswith("_"):
            continue

        module_name = f"subscribers.{filename[:-3]}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            logger.exception(f"Failed to import {module_name}")
            continue

        module_found = False
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Subscriber) and obj is not Subscriber:
                try:
                    instance = obj()
                    publisher.register(instance)
                    found += 1
                    module_found = True
                except Exception:
                    logger.exception(f"Failed to instantiate {obj.__name__}")

        if not module_found:
            logger.debug(f"No Subscriber subclass found in {module_name}, skipping")

    if found == 0:
        logger.warning("No subscribers found in subscribers/ directory")
    else:
        logger.info(f"Loaded {found} subscriber(s)")
