from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Telegram
    TG_API_ID: int
    TG_API_HASH: str
    TG_SESSION_NAME: str = "tg_session"
    TG_PROXY: str | None = None  # socks5://host:port or http://host:port
    CHANNELS_TO_WATCH: list[str] = ["theblockbeats", "Odaily_News", "WatcherGuru"]

    # Forwarding
    WEBHOOK_URL: str = "http://127.0.0.1:8101/receive"

    # Sentiment API
    SENTIMENT_API_URL: str = ""
    SENTIMENT_API_KEY: str = ""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8101

    # Logging
    LOG_LEVEL: str = "INFO"


settings = Settings()
