## Context

The tg2fastapi project uses a pub/sub architecture where Telegram messages are received by a Telethon client and broadcast to registered subscribers. Subscribers are auto-discovered from the `subscribers/` directory. Currently two subscribers exist: `ExampleLoggerSubscriber` (logging) and `WebhookSubscriber` (HTTP forwarding). There is no local persistence mechanism.

The incoming message model `TGMessage` has fields: `channel`, `message_id`, `text`, `date`, `media`. The new subscriber needs to map these to CSV columns: `channelName` (from `channel`), `content` (from `text`), `time` (from `date`).

## Goals / Non-Goals

**Goals:**
- Provide a simple local CSV persistence subscriber that follows existing patterns
- Auto-create CSV file with headers on first write
- Append rows atomically without corrupting existing data
- Handle concurrent writes safely (single async event loop, sequential per subscriber)

**Non-Goals:**
- CSV file rotation or size management
- Configurable column mapping
- Support for other output formats (JSON, SQLite, etc.)
- Media file downloading or storage

## Decisions

**1. CSV file location**: Store as `data/messages.csv` relative to project root.
- *Rationale*: Separates data from code. The `data/` directory is a common convention.
- *Alternative*: Store in `logs/` — rejected because logs are for operational data, not message content.

**2. Use Python stdlib `csv` module**: No external dependencies.
- *Rationale*: CSV writing is simple enough that stdlib handles it well. Avoids adding pandas/polars as a dependency for a trivial operation.
- *Alternative*: `aiofiles` for async I/O — rejected because CSV appends are fast enough that blocking I/O in an async context is acceptable for this use case.

**3. File open/close per write**: Open the file in append mode for each message, write, and close.
- *Rationale*: Ensures data is flushed to disk after each message. Prevents data loss on crash. Simpler than managing a persistent file handle.
- *Alternative*: Keep file handle open — rejected due to crash safety concerns.

**4. Column mapping**: `channel` → `channelName`, `text` → `content`, `date` → `time`.
- *Rationale*: Matches the user's requested column names exactly.

## Risks / Trade-offs

- **[Disk space]** → CSV file grows unbounded. Mitigation: out of scope for now; users can manually rotate or add rotation later.
- **[Blocking I/O in async loop]** → File write blocks the event loop briefly. Mitigation: CSV append is microseconds; acceptable for message volumes from Telegram channels.
- **[Special characters in text]** → Message text may contain newlines, commas, quotes. Mitigation: Python's `csv.writer` handles quoting automatically.
