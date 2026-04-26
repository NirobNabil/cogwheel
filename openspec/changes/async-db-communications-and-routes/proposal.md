## Why

The API currently mixes synchronous route handlers and synchronous SQLAlchemy sessions inside an ASGI application. Moving all route execution and database communication to async prevents blocking the event loop under concurrent load and aligns the service with FastAPI's async runtime model.

## What Changes

- Convert every API route handler, including health, transaction, analytics, and upload routes, to `async def`.
- Replace synchronous database engine/session wiring with async SQLAlchemy engine and async session dependencies.
- Convert repository and service database calls to awaitable async operations.
- Preserve existing API request/response contracts, validation behavior, transaction semantics, and error handling.
- Update tests and test database fixtures to exercise async sessions and async route behavior.
- Update runtime configuration and documentation so database URLs, local development, Docker, and migrations remain clear with the async database stack.

## Capabilities

### New Capabilities

- `async-api-routes`: Defines the requirement that all FastAPI routes execute asynchronously while preserving existing public API behavior.
- `async-database-communications`: Defines async database engine, session, repository, service, and transaction behavior for all database interactions.

### Modified Capabilities

- None.

## Impact

- Affected runtime code: `infrastructure/main.py`, `infrastructure/routes/**`, `infrastructure/configuration/db_config.py`, `app/core/service/**`, and `data/repository/**`.
- Affected tests: API tests, transaction rollback tests, migration tests, and shared test fixtures.
- Affected dependencies/configuration: SQLAlchemy async engine/session usage and any required async database driver/test driver configuration.
- Public API paths and payload schemas should remain unchanged.
