## ADDED Requirements

### Requirement: CSV subscriber auto-discovery
The `SaveToLocalSubscriber` class in `subscribers/saveToLocal.py` SHALL inherit from `Subscriber` and be auto-discovered by the existing loader mechanism on application startup.

#### Scenario: Subscriber is registered on startup
- **WHEN** the application starts and `subscribers/saveToLocal.py` exists
- **THEN** `SaveToLocalSubscriber` SHALL be discovered, instantiated, and registered with the Publisher

### Requirement: Message persistence to CSV
The subscriber SHALL append each received `TGMessage` as a row to a CSV file with columns `channelName`, `content`, `time`.

#### Scenario: First message creates file with headers
- **WHEN** the subscriber receives a message and the CSV file does not exist
- **THEN** the subscriber SHALL create the file with a header row (`channelName,content,time`) followed by the message data row

#### Scenario: Subsequent messages append to existing file
- **WHEN** the subscriber receives a message and the CSV file already exists
- **THEN** the subscriber SHALL append a new row without rewriting headers

#### Scenario: Column mapping from TGMessage
- **WHEN** a `TGMessage` with `channel="testchannel"`, `text="hello world"`, `date="2026-02-21T15:30:00+00:00"` is received
- **THEN** the CSV row SHALL contain `channelName="testchannel"`, `content="hello world"`, `time="2026-02-21T15:30:00+00:00"`

### Requirement: CSV data integrity
The subscriber SHALL produce valid CSV output that handles special characters in message text.

#### Scenario: Message text contains commas and newlines
- **WHEN** a message with text containing commas, newlines, or double quotes is received
- **THEN** the CSV output SHALL properly quote the field per RFC 4180

### Requirement: CSV file location
The subscriber SHALL write to `data/messages.csv` relative to the project root directory. The `data/` directory SHALL be created automatically if it does not exist.

#### Scenario: Data directory does not exist
- **WHEN** the subscriber writes its first message and `data/` directory is missing
- **THEN** the subscriber SHALL create the `data/` directory before writing the CSV file

### Requirement: Error isolation
The subscriber SHALL NOT propagate exceptions to the Publisher. Errors during file I/O SHALL be logged and the subscriber SHALL return gracefully.

#### Scenario: File write fails due to permissions
- **WHEN** the CSV file cannot be written (e.g., permission denied)
- **THEN** the subscriber SHALL log the error and return without raising an exception
