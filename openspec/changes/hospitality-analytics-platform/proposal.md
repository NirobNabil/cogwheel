## Why

The company receives recurring hospitality operations and sales data from multiple sources, but lacks a centralized backend for storing, querying, and analyzing that data. This change defines a lightweight FastAPI service that supports transaction ingestion, CSV uploads, filtered retrieval, and basic revenue analytics in a Dockerized runtime.

## What Changes

- Add a FastAPI backend for hospitality transaction data.
- Add transaction creation via `POST /transactions`.
- Add bulk transaction creation via JSON using `POST /transactions/bulk`.
- Add CSV upload ingestion via `POST /transactions/upload-csv`, compatible with Swagger UI file upload.
- Add transaction listing via `GET /transactions` with optional `category`, `start_date`, and `end_date` filters.
- Add analytics endpoints for total sales and top properties by revenue.
- Add persistence using SQLAlchemy with PostgreSQL.
- Add Alembic migrations for database schema management.
- Use floating-point `price` values for this assignment.
- Accept and return transaction dates in `DD-MM-YYYY` format.
- Wrap database write interactions in ACID transactions with explicit commit on success and rollback on failure, following the core service pattern.
- Add Docker support for the API plus a PostgreSQL container with a persisted Docker volume.
- Use a simplified structure inspired by `demo/kraits-core-service`: `infrastructure/` for runtime wiring, `app/core/` for schemas/services, `data/` for models/repositories, and `alembic/` for migrations.
- Add simple request-id-aware console logging based on the core service logging setup.
- Add VS Code debug configuration following the core service `launch.json` style.
- Add a Bruno collection with request variations for every API so manual verification is concrete and repeatable.
- Add unit tests that the AI must run when verifying implementation changes.
- Exclude JWT authentication and protected routes from this change, including any bonus auth objective.
- Keep implementation intentionally small for the assignment; do not introduce RBAC, interceptors, scanners, external gateways, or broad enterprise middleware from the reference service.

## Capabilities

### New Capabilities

- `transaction-records`: Defines the transaction data model, single-record creation, validation, persistence, and filtered listing behavior.
- `bulk-transaction-ingestion`: Defines JSON bulk ingestion and CSV upload ingestion behavior, including valid-record handling and error reporting.
- `business-analytics`: Defines revenue analytics behavior for total sales and top properties.
- `containerized-service`: Defines Docker build and runtime behavior for the FastAPI service.
- `database-migrations`: Defines PostgreSQL schema management through Alembic migrations.
- `database-transactions`: Defines ACID transaction handling for database interactions.
- `developer-workflow`: Defines the local debugging and project-structure conventions for this service.
- `verification-workflow`: Defines Bruno manual API coverage and unit-test verification expectations.

### Modified Capabilities

- None.

## Impact

- New Python FastAPI application structure.
- New SQLAlchemy database models, session management, and Alembic migration behavior.
- New request and response schemas for transaction and analytics APIs.
- New CSV parsing and validation path for bulk upload from API clients and Swagger UI.
- New application dependencies for FastAPI, SQLAlchemy, ASGI serving, multipart uploads, and testing.
- New Dockerfile, Docker Compose configuration, PostgreSQL volume, and runtime environment configuration.
- New VS Code debug configuration.
- New Bruno collection and environments covering all API variations.
- New unit tests covering validation, persistence, filtering, ingestion, analytics calculations, transaction rollback behavior, migrations, and startup assumptions.

## Resolved Decisions

- Should the default persistence target remain SQLite for the assignment, or should PostgreSQL be used from the start? 
  - postgresql should be used. use a postgres docker container with volume 
- Should bulk and CSV ingestion be all-or-nothing on any invalid record, or should the API store valid rows and report invalid rows?
  - store valid rows and report invalid rows
- Should `date` represent a calendar date only, or should it support timestamps with time zones?
  - calendar date only. no timezone
- Should analytics endpoints support the same filters as `GET /transactions`, or only aggregate across all stored data?
  - only aggregate across all stored data
- Should transaction `price` be stored as decimal money values instead of floating-point values?
  - updated decision: use floating-point prices for this assignment.
- Should manual verification be done through Bruno?
  - yes. add a Bruno collection with variations for every API.
- Should AI verification use unit tests?
  - yes. implementation verification should include unit tests.
- What date format should the API use?
  - use `DD-MM-YYYY`.
- How should database writes be handled?
  - use ACID transactions with commit on success and rollback on failure, following the core service pattern.

## Implementation Constraints

- Prefer simple assignment-friendly code over exhaustive edge-case handling.
- Reuse the reference service's structure and conventions only where they improve familiarity.
- Keep controllers thin, services focused on business logic, and repositories focused on database access.
- Use Alembic instead of `metadata.create_all()` for schema creation.
- Use Bruno request collections for manual API verification instead of vague manual steps.
- Use unit tests as the AI verification path after implementation changes.
- Do not copy RBAC, JWT, route interceptors, scanner integrations, gateways, Helm, or production observability complexity from the reference service.
