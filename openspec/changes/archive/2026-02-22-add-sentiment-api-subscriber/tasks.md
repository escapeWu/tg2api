## 1. Configuration

- [x] 1.1 Add `SENTIMENT_API_URL` and `SENTIMENT_API_KEY` to `app/config.py` Settings class
- [x] 1.2 Add `SENTIMENT_API_URL` and `SENTIMENT_API_KEY` entries to `.env.example`

## 2. Subscriber Implementation

- [x] 2.1 Create `subscribers/sentiment_api.py` with `SentimentApiSubscriber` class that maps TGMessage to sentiment API schema and POSTs with Bearer auth

## 3. Testing

- [x] 3.1 Test the subscriber by running the application and verifying data appears in the remote API
