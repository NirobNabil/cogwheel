## Context

The service is a FastAPI application running on an ASGI server. Most current route handlers are synchronous and depend on a synchronous SQLAlchemy `Session` created from a synchronous engine. Repository functions call blocking session methods such as `commit`, `refresh`, `scalars`, `scalar`, and `execute`.

The async conversion is cross-cutting because request handlers, dependency injection, service functions, repository functions, tests, and local database configuration all need to agree on the same async session model.

## Goals / Non-Goals

**Goals:**

- Ensure every public route handler is declared and executed as `async def`.
- Use SQLAlchemy async engine and `AsyncSession` for all application database communication.
- Keep existing endpoint paths, payload schemas, validation rules, transaction rollback behavior, and response shapes unchanged.
- Keep migrations managed by Alembic without requiring the application to create tables at startup.
- Update automated tests so async database behavior is verified rather than only wrapped by synchronous test helpers.

**Non-Goals:**

- Changing the public API contract or adding new endpoints.
- Redesigning the transaction, analytics, CSV parsing, or validation domain behavior.
- Introducing authentication, background workers, caching, or broad middleware changes.
- Making Alembic migration execution itself asynchronous unless required by the selected driver configuration.

## Decisions

1. Use SQLAlchemy `AsyncEngine`, `async_sessionmaker`, and `AsyncSession` for runtime database access.

   Rationale: this keeps the existing SQLAlchemy ORM model and query style while removing blocking DB calls from request execution.

   Alternatives considered:
   - Keep synchronous SQLAlchemy and only mark routes async. This would still run blocking database operations in the event loop.
   - Replace SQLAlchemy with a different async data-access library. That would increase scope and risk without improving the requested behavior.

2. Implement the FastAPI database dependency as an async generator.

   Rationale: FastAPI can manage async dependency cleanup directly, and `async with SessionLocal()` guarantees the session is closed after each request.

   Alternatives considered:
   - Manually close sessions in route handlers. This would duplicate lifecycle management and make controller code less consistent.

3. Convert service and repository database-facing functions to async and require callers to `await` them.

   Rationale: it keeps controllers thin while making await boundaries explicit through the service and repository layers.

   Alternatives considered:
   - Run synchronous repository calls in a thread pool. That would preserve sync code but retain a mixed execution model and reduce the value of an async DB stack.

4. Preserve explicit transaction semantics for write operations.

   Rationale: current behavior commits once on successful writes, rolls back on write failures, and avoids commit/rollback for read endpoints. The async implementation should keep those observable guarantees using `await db.commit()`, `await db.rollback()`, and `await db.refresh(record)`.

   Alternatives considered:
   - Use automatic transaction blocks everywhere. That could be valid, but it would change the current explicit transaction-call behavior that tests already verify.

5. Keep Alembic migration configuration compatible with local and Docker workflows.

   Rationale: the application can use async runtime database access while Alembic continues to run predictably during setup and container startup. If the runtime async driver URL differs from Alembic's expected sync URL, settings should document or derive the correct variant.

   Alternatives considered:
   - Convert Alembic to fully async execution. This is unnecessary unless the chosen URL/driver cannot support the current migration path.

## Risks / Trade-offs

- Async and sync URL mismatch -> Document supported URL formats and normalize configuration where needed so runtime and migrations both connect reliably.
- Partial conversion leaves blocking calls in the event loop -> Search for remaining synchronous `Session`, `create_engine`, and blocking session method usage during implementation.
- Tests pass through synchronous helpers only -> Update fixtures to use async sessions and async cleanup so they exercise the same path as production.
- Async test dependencies add setup complexity -> Keep dependencies minimal and use the same database backend pattern as existing tests where possible.

## Migration Plan

1. Add or confirm the required async database driver dependency for the configured PostgreSQL URL and the test database URL.
2. Replace runtime database wiring with `create_async_engine`, `async_sessionmaker`, and an async `get_db` dependency.
3. Convert route handlers, service functions, and repository functions to async from the controller boundary down to all database calls.
4. Update tests and fixtures to override the async dependency and verify existing behavior, including rollback and read-only endpoint semantics.
5. Update README, `.env.example`, Docker, or Alembic documentation where URL formats or startup commands change.
6. Run the full automated test suite and fix any regressions before applying the change.

Rollback is code-level: revert to the synchronous engine/session implementation and synchronous route/service/repository functions if the async conversion causes runtime issues before release.

## Open Questions

- Which async database driver should be standardized for local tests if the current PostgreSQL driver is not sufficient for all async SQLAlchemy paths?
