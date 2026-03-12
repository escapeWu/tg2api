## ADDED Requirements

### Requirement: Forward TG messages to remote sentiment API
The system SHALL send each received TGMessage to the sentiment API endpoint (`POST /api/sentiment`) with proper field mapping and Bearer token authentication.

#### Scenario: Successful forwarding
- **WHEN** a TGMessage is received with text content
- **THEN** the subscriber SHALL POST to `{SENTIMENT_API_URL}/api/sentiment` with title (first line of text), content (full text), opinion (empty string), create_time (message date), and relation (channel name)

#### Scenario: API returns error
- **WHEN** the sentiment API returns a non-2xx status or is unreachable
- **THEN** the subscriber SHALL log the error and continue without raising an exception

#### Scenario: Empty text message
- **WHEN** a TGMessage has empty text
- **THEN** the subscriber SHALL use `"{channel}-{message_id}"` as the title fallback

### Requirement: Configuration via environment variables
The system SHALL read `SENTIMENT_API_URL` and `SENTIMENT_API_KEY` from environment variables for the remote API connection.

#### Scenario: Configuration present
- **WHEN** both `SENTIMENT_API_URL` and `SENTIMENT_API_KEY` are set
- **THEN** the subscriber SHALL use these values for API requests with Bearer token auth

#### Scenario: Default URL
- **WHEN** `SENTIMENT_API_URL` is not set
- **THEN** the system SHALL use an empty string default (subscriber effectively disabled)
