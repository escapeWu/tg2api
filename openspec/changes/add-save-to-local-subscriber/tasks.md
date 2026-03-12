## 1. Setup

- [x] 1.1 Create `data/` directory and add `data/` to `.gitignore`

## 2. Core Implementation

- [x] 2.1 Create `subscribers/saveToLocal.py` with `SaveToLocalSubscriber` class inheriting from `Subscriber`
- [x] 2.2 Implement `send()` method: map TGMessage fields to CSV columns (`channelName`, `content`, `time`)
- [x] 2.3 Implement auto-creation of `data/` directory and CSV file with headers on first write
- [x] 2.4 Implement append-mode writing for subsequent messages
- [x] 2.5 Add error handling: catch and log I/O exceptions without propagating

## 3. Verification

- [x] 3.1 Start the app and verify `SaveToLocalSubscriber` is auto-discovered and registered
- [x] 3.2 Send a test message and verify CSV file is created with correct headers and data
- [x] 3.3 Verify messages with special characters (commas, newlines, quotes) are properly quoted in CSV
