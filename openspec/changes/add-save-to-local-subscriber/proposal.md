## Why

Currently the system only logs messages or forwards them via HTTP webhook. There is no built-in way to persist Telegram messages locally for offline analysis, auditing, or historical review. A local CSV subscriber provides a simple, zero-dependency persistence layer that users can open in any spreadsheet tool.

## What Changes

- Add a new subscriber `SaveToLocalSubscriber` in `subscribers/saveToLocal.py`
- The subscriber appends each incoming message as a row to a local CSV file
- CSV columns: `channelName`, `content`, `time`
- CSV file is created automatically on first write with headers
- Uses the existing subscriber auto-discovery mechanism — no core code changes needed

## Capabilities

### New Capabilities
- `csv-local-storage`: Subscriber that persists Telegram messages to a local CSV file with columns channelName, content, and time

### Modified Capabilities
<!-- No existing spec requirements are changing -->

## Impact

- New file: `subscribers/saveToLocal.py`
- Runtime: creates/appends to a CSV file on disk (default location in project data directory)
- No changes to core app, models, or existing subscribers
- No new dependencies (uses Python stdlib `csv` module)
