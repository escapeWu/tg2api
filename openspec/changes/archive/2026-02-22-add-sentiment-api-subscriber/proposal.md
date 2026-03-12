## Why

Telegram channel messages are currently only stored locally or forwarded via webhook. We need to archive sentiment data to a centralized remote platform (`example.com`) for persistent storage and cross-system querying.

## What Changes

- Add a new subscriber `SentimentApiSubscriber` that POSTs TG messages to the remote sentiment API
- Add configuration for the remote API base URL and API key
- Map TGMessage fields to the sentiment API schema (title, content, opinion, create_time, relation)

## Capabilities

### New Capabilities
- `sentiment-api-forwarding`: Subscriber that forwards TG messages to the remote sentiment API endpoint with authentication and field mapping

### Modified Capabilities
<!-- None - no existing spec requirements change -->

## Impact

- New file: `subscribers/sentiment_api.py`
- Modified: `app/config.py` (new env vars), `.env.example` (new env vars)
- New dependency: `httpx` (already in use)
