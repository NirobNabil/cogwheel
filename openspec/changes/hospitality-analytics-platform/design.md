## Context

This is a new lightweight backend for hospitality transaction data. The assignment requires a Python FastAPI service that accepts individual and bulk transactions, stores them in a database, exposes filtered reads, calculates simple revenue analytics, accepts CSV uploads through Swagger UI, and runs in Docker.

The reference service at `demo/kraits-core-service` is intentionally much larger than this assignment. This design adopts only the familiar structural conventions: `infrastructure/` for app startup, routes, settings, logging, and DB wiring; `app/core/` for schemas and services; `data/` for models and repositories; and `alembic/` for migrations. It explicitly avoids importing the reference service's RBAC, JWT, gateway, scanner, Helm, and production observability complexity.

## Goals / Non-Goals

**Goals:**

- Provide a simple FastAPI application with OpenAPI/Swagger UI support.
- Use PostgreSQL as the database, running locally through Docker with a persisted volume.
- Manage database schema with Alembic migrations.
- Validate transaction input consistently across single-create, JSON bulk, and CSV upload paths.
- Store valid rows and report invalid rows for both JSON bulk and CSV ingestion.
- Support filtered transaction listing by category and `DD-MM-YYYY` calendar date range.
- Calculate global analytics as `price * quantity` with floating-point prices.
- Use explicit transaction boundaries for database work, with commit on success and rollback on failure.
- Use a small controller -> service -> repository flow similar to the reference repo.
- Add request-id-aware console logging based on the reference logging setup.
- Add `.vscode/launch.json` for local uvicorn debugging.
- Add a Bruno collection with request variations for every endpoint.
- Add unit tests and require them for AI-side verification.
- Keep the code compact and readable for an assignment.

**Non-Goals:**

- JWT authentication, protected routes, user accounts, RBAC, or route interceptors.
- Full parity with `kraits-core-service` architecture.
- Complex exception hierarchies, scanner/gateway integrations, Redis, Helm, OpenTelemetry, or Kubernetes deployment.
- Exhaustive edge-case handling beyond reasonable request validation and clear ingestion summaries.
- Analytics filters; analytics aggregate across all stored transactions only.
- Production-grade financial precision; floating point is accepted for this assignment by user decision.

## Decisions

### Use a simplified core-service-inspired folder structure

The implementation should use this structure:

```text
infrastructure/
  main.py
  configuration/
    db_config.py
    log_config.py
    middleware.py
  routes/
    api_router.py
    controller/
      transaction_controller.py
      analytics_controller.py
  settings/
    settings.py
app/
  core/
    schema/
      transaction_schema.py
      analytics_schema.py
    service/
      transaction_service.py
      analytics_service.py
data/
  model/
    transaction_model.py
  repository/
    transaction_repository.py
alembic/
  versions/
```

Rationale: This preserves the reference repo's navigation style while keeping the assignment code small.

Alternative considered: A single-file FastAPI app. This is shortest, but it does not match the structure the user is already familiar with.

### Keep controllers thin and avoid enterprise middleware

Controllers should define request/response behavior, inject the DB session, call services, and return schemas. Services should hold validation orchestration and business calculations. Repositories should hold SQLAlchemy queries.

Rationale: This mirrors the reference controller -> service -> repository flow without adding RBAC decorators, token dependencies, or route interceptors.

Alternative considered: Put all logic directly in route functions. This is simpler initially but becomes harder to follow once CSV parsing and analytics queries are added.

### Use synchronous SQLAlchemy for this assignment

Use standard SQLAlchemy `Session` with PostgreSQL rather than async SQLAlchemy.

Rationale: The reference service uses async SQLAlchemy, but synchronous SQLAlchemy is easier for a small assignment, Alembic setup, and tests/manual debugging. The folder structure remains familiar without copying unnecessary async complexity.

Alternative considered: Use async SQLAlchemy and `asyncpg` exactly like the reference repo. This is familiar in shape but adds complexity that is not needed here.

### Use PostgreSQL through Docker Compose with a named volume

Local development should provide a `postgres` service in `docker-compose.yml` with a named volume for persisted data. The API should read `DATABASE_URL` from `.env`, with a documented local default suitable for Compose.

Rationale: The user's clarified answer requires PostgreSQL and a Docker volume. A single `DATABASE_URL` is simpler than the reference service's multiple DB environment variables.

Alternative considered: Keep SQLite by default. This is simpler but conflicts with the resolved decision.

### Use Alembic for schema management

Create an initial Alembic migration for the transactions table and use `alembic upgrade head` to apply schema changes. Do not use `Base.metadata.create_all()` for runtime schema creation.

Rationale: The user explicitly requested Alembic, and this matches the reference repo's migration approach.

Alternative considered: Auto-create tables on startup. This is fast for demos but hides migration behavior and conflicts with the requested setup.

### Store price as floating point

The transaction model should store `price` as a floating-point value and validate API values as positive numbers. Revenue should always be calculated as `price * quantity`.

Rationale: The user explicitly updated the decision to use floating-point money for this assignment, prioritizing simplicity over production financial precision.

Alternative considered: Use PostgreSQL `Numeric` and Python `Decimal`. This is better for production money handling but is not the desired assignment behavior.

### Treat `date` as a `DD-MM-YYYY` calendar date

The API should accept and return transaction dates as `DD-MM-YYYY` values. Internally, the database can store a native PostgreSQL `DATE`, but API schemas and Bruno examples should use the user-facing `DD-MM-YYYY` format.

Rationale: The user clarified that dates are calendar-only and later specified `DD-MM-YYYY` as the API format.

Alternative considered: Use timestamps. This adds timezone and boundary behavior that the assignment does not require.

### Use explicit ACID transaction handling for database writes

Database write paths should follow the core service style: perform related inserts in one SQLAlchemy session transaction, commit after successful persistence, and rollback if a database exception occurs. Partial-success ingestion should validate records first, then persist the valid records in one transaction and report invalid records without attempting to insert them.

Rationale: This keeps write behavior predictable and mirrors the reference service's explicit commit/rollback pattern without copying its broader complexity.

Alternative considered: Let request-scoped dependencies auto-commit. This is less explicit and does not match the user's requested style.

### Use partial-success ingestion for JSON bulk and CSV

Both `POST /transactions/bulk` and `POST /transactions/upload-csv` should store valid records and report invalid records. Keep the response simple: inserted count, failed count, created records or IDs, and row/item errors.

Rationale: The user clarified that valid rows should be stored while invalid rows are reported.

Alternative considered: Make JSON bulk atomic. This is easier to reason about transactionally but conflicts with the clarified behavior.

### Keep analytics global

Analytics endpoints should aggregate across all persisted transactions and not accept category or date filters.

Rationale: The user clarified that analytics should aggregate across all stored data.

Alternative considered: Reuse transaction filters for analytics. This is useful but outside the assignment scope.

### Use simple request-id logging

Add request ID middleware and a compact logging configuration based on `infrastructure/configuration/log_config.py` in the reference service. Keep console logging only; no OpenTelemetry or external log shipping.

Rationale: The reference logging setup is familiar and useful for debugging, but production observability is unnecessary.

Alternative considered: Default Python logging only. This is simpler but loses request correlation.

### Add VS Code uvicorn debugging

Add `.vscode/launch.json` following the reference shape: Python launch config, `module: uvicorn`, `infrastructure.main:app`, reload enabled, host `0.0.0.0`, port `8000`, workspace cwd, `.env` file, and `PYTHONPATH`.

Rationale: This matches the user's existing debugging workflow while changing the app module and port for this assignment.

Alternative considered: Document command-line debugging only. This is less convenient for the user.

### Add Bruno manual verification coverage

Add a Bruno collection under `bruno/hospitality-analytics-platform/` with `bruno.json`, synced `environments/Local.bru` and `environments/Local.json`, and grouped request files for Transactions, Bulk Upload, CSV Upload, and Analytics. Requests should cover successful and invalid variations for every API, using environment variables such as `baseUrl`, `category`, `startDate`, `endDate`, and captured created transaction IDs.

Rationale: Manual verification should be executable and repeatable, not a vague checklist.

Alternative considered: Use only Swagger UI. Swagger is useful for ad hoc exploration but does not preserve a structured set of test variations.

### Use unit tests for AI verification

Add unit tests with a lightweight test database setup so implementation verification can run through automated tests. The AI should run the unit test command after code changes and report results.

Rationale: Bruno is for manual verification by the user; unit tests are the reliable verification path for implementation work.

Alternative considered: Manual-only verification. This misses regressions and makes implementation completion subjective.

## Risks / Trade-offs

- PostgreSQL plus Alembic adds setup steps -> Provide `docker-compose.yml`, `.env.example`, and README commands.
- Sync SQLAlchemy differs from the reference async DB layer -> Accepted for simpler assignment code while preserving the same layers and naming.
- Partial-success ingestion can surprise clients expecting all-or-nothing -> Return clear inserted and failed counts with item or row errors.
- Floating-point prices can have rounding artifacts -> Accept this assignment trade-off and avoid extra financial-precision code.
- `DD-MM-YYYY` is not the native JSON date convention -> Add schema parsing/serialization helpers and Bruno examples using this exact format.
- Explicit transaction handling can add boilerplate -> Keep commit/rollback handling in repository/service write paths only.
- Docker `run` alone needs a reachable PostgreSQL database -> Prefer Docker Compose for local full-stack runtime and document `DATABASE_URL` when running only the API image.
- Request-id logging adds middleware code -> Keep it small and limited to console logs.
- Bruno coverage can become noisy -> Keep request groups small and focused on assignment endpoints only.

## Migration Plan

1. Add the simplified folder structure.
2. Add settings, DB session configuration, logging configuration, and middleware.
3. Add the transaction model and initial Alembic migration.
4. Add transaction, bulk ingestion, CSV upload, and analytics APIs.
5. Add ACID commit/rollback handling for write operations.
6. Add Dockerfile, Docker Compose PostgreSQL service with volume, `.env.example`, and README commands.
7. Add `.vscode/launch.json` for uvicorn debugging.
8. Add Bruno request collection with endpoint variations.
9. Add unit tests and run them during implementation verification.

Rollback is straightforward because this is a new service: remove the added application files, migration files, Docker files, and development configuration. Local PostgreSQL data can be removed by deleting the Docker volume if needed.

## Open Questions

- None blocking. The implementation should prefer simple assignment-friendly behavior when a minor edge case is not specified.
