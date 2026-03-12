## Context

The tg2fastapi project uses a pub/sub pattern where subscribers auto-discovered from `subscribers/` receive TGMessage objects. The remote platform at `example.com` exposes a sentiment API (`POST /api/sentiment`) that accepts JSON with fields: title, content, opinion, create_time, relation. Authentication uses an API key via Bearer token header.

## Goals / Non-Goals

**Goals:**
- Forward TG messages to the remote sentiment API as sentiment records
- Map TGMessage fields to the sentiment API schema
- Support configuration via environment variables

**Non-Goals:**
- Batch uploading or queuing of messages
- Reading back sentiment data from the API
- Attachment uploads

## Decisions

- **Field mapping**: `TGMessage.text` → first line as `title`, full text as `content`, channel name as `relation`, `date` as `create_time`, empty string as `opinion` (raw message, no analysis). Rationale: keeps it simple and lossless.
- **Auth method**: Bearer token in Authorization header per the API's HTTPBearer security scheme. The API key is stored in env var `SENTIMENT_API_KEY`.
- **Error handling**: Log and skip on failure (consistent with existing WebhookSubscriber pattern). No retries.

## Risks / Trade-offs

- [API downtime] → Messages are lost if API is down. Acceptable for now; queuing is a future enhancement.
- [Title extraction from first line] → May be empty for media-only messages. Mitigation: fallback to channel name + message_id.
