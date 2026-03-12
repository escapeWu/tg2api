from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, model_validator

from app.logging_config import get_logger
from app.models import TGMessage

logger = get_logger("api")

app = FastAPI(title="TG Message Receiver")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body_bytes = await request.body()
    body_text = body_bytes.decode("utf-8", errors="replace")
    logger.error(
        "422 validation error on %s %s | body=%s | errors=%s",
        request.method,
        request.url.path,
        body_text,
        exc.errors(),
    )
    return await request_validation_exception_handler(request, exc)


@app.post("/receive")
async def receive_message(msg: TGMessage, request: Request):
    logger.info(f"Received message from @{msg.channel}: {msg.text[:50]}...")
    return {"status": "success"}


@app.post("/inject")
async def inject_message(msg: TGMessage, request: Request):
    """Inject a message directly into the publisher pipeline (for testing)."""
    await request.app.state.publisher.publish(msg)
    return {"status": "ok"}


class SendRequest(BaseModel):
    target: str | None = None
    targets: List[str] | None = None
    text: str
    image_url: str | None = None
    image_path: str | None = None

    @model_validator(mode="after")
    def validate_targets(self):
        if self.target and self.targets:
            raise ValueError("Provide either 'target' or 'targets', not both")
        if not self.target and not self.targets:
            raise ValueError("Either 'target' or 'targets' is required")
        if self.targets is not None and len(self.targets) == 0:
            raise ValueError("'targets' must not be empty")
        return self


@app.post("/send")
async def send_message_endpoint(req: SendRequest, request: Request):
    """Send message(s) to one or multiple Telegram chats.

    Supports:
    - text: Message text (required)
    - target: single destination (optional)
    - targets: multiple destinations (optional)
    - image_url: URL of image to send (optional)
    - image_path: Local file path of image to send (optional)

    If both image_url and image_path are provided, image_url takes precedence.
    """
    from app.telegram import send_message

    client = request.app.state.tg_client
    target_list = req.targets if req.targets is not None else [req.target]
    try:
        results = []
        for target in target_list:
            result = await send_message(
                client,
                target,
                req.text,
                image_url=req.image_url,
                image_path=req.image_path
            )
            results.append(result)

        if req.targets is not None:
            logger.info("Sent message to %d targets", len(results))
            return {"results": results, "count": len(results)}

        logger.info(f"Sent message to {req.target!r} (msg_id={results[0]['message_id']})")
        return results[0]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
