# Notifications Module

Consumes domain events (via the transactional outbox pattern) and routes them to user-configured channels (In-App, Email, Slack).

## Architecture
The system consists of two distinct runtime components deployed from the same codebase:
1. **API Server (`main.py`)**: A standard FastAPI application serving the `GET /notifications` and `PUT /preferences` endpoints for the React frontend.
2. **Outbox Worker (`outbox_consumer.py`)**: A long-lived Python worker that polls the `outbox_events` table in PostgreSQL.

## At-Least-Once Delivery & Idempotency
Because network failures can occur between reading from the outbox and committing the notification write, the `outbox_consumer` is designed around **At-Least-Once** semantics.

If the consumer crashes and restarts, it will replay the outbox event.
To prevent duplicate notifications from spamming users during a replay, the `CreateNotificationFromEventUseCase` implements an idempotent barrier. It relies on a database unique constraint on `(event_id, user_id, channel)`. If it catches a UniqueViolation, it logs a `DuplicateNotificationError` and silently skips processing, guaranteeing the user is only notified exactly once per domain event.

## Low Latency Consumption
Instead of polling the database every 10 seconds (which wastes resources and adds latency), the outbox consumer is designed to use **PostgreSQL LISTEN/NOTIFY**. When the Failure Analyzer module commits a row to `outbox_events`, it issues a `NOTIFY` command. The outbox consumer receives this instantly, drops its sleep cycle, and processes the batch, resulting in sub-2-second notification delivery latency while maintaining zero CPU overhead during idle periods.
