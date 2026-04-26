## 1. Async Database Wiring

- [x] 1.1 Add or confirm required async database driver dependencies for PostgreSQL runtime and async test database usage.
- [x] 1.2 Replace synchronous SQLAlchemy engine/session setup in `infrastructure/configuration/db_config.py` with async engine, async session factory, and `AsyncSession` typing.
- [x] 1.3 Convert `get_db` to an async generator dependency that yields an `AsyncSession` and closes it with async context management.
- [x] 1.4 Confirm Alembic migration configuration still runs against the configured database URL, adding URL normalization or documentation if runtime and migration URLs differ.

## 2. Async Repository and Service Layer

- [x] 2.1 Convert transaction repository functions that perform database I/O to async functions using `AsyncSession`.
- [x] 2.2 Await async commit, rollback, refresh, scalar, scalars, and execute calls in repository read and write paths.
- [x] 2.3 Preserve write transaction semantics: one commit on successful writes, rollback on write failures, and refreshed records before returning.
- [x] 2.4 Convert transaction service functions that call repositories to async functions and await repository operations.
- [x] 2.5 Convert analytics service functions to async functions and await repository analytics queries.

## 3. Async Route Handlers

- [x] 3.1 Convert the health endpoint and every transaction and analytics route handler to `async def`.
- [x] 3.2 Update route dependencies to receive `AsyncSession` from the async database dependency.
- [x] 3.3 Await all async service calls from route handlers, including CSV upload ingestion after async file reading.
- [x] 3.4 Verify no database-backed route returns unresolved awaitables or calls synchronous database-facing service functions.

## 4. Tests and Documentation

- [x] 4.1 Update API test fixtures to override the async database dependency with async-compatible sessions.
- [x] 4.2 Update transaction rollback tests to verify async commit, rollback, and read-only session behavior.
- [x] 4.3 Add or update route inspection coverage proving application endpoint handlers are async coroutine functions.
- [x] 4.4 Update README, `.env.example`, Docker notes, or test setup notes for any async database URL or driver changes.
- [x] 4.5 Run the full automated test suite and fix regressions.
