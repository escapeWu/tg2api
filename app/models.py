from pydantic import BaseModel


class TGMessage(BaseModel):
    channel: str
    message_id: int
    text: str
    date: str
    media: bool = False
