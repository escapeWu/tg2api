import logging
import os
from logging.handlers import RotatingFileHandler

_configured = False


def setup_logging(level: str = "INFO") -> None:
    global _configured
    if _configured:
        return
    _configured = True

    log_level = getattr(logging, level.upper(), logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    root = logging.getLogger()
    root.setLevel(log_level)

    # Suppress noisy third-party loggers
    for name in ("telethon", "urllib3", "httpcore", "httpx", "uvicorn.access"):
        logging.getLogger(name).setLevel(max(log_level, logging.WARNING))

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(formatter)
    root.addHandler(console)

    # File handler
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
