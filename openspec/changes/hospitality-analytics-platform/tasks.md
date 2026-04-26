## 1. Project Skeleton

- [x] 1.1 Create the simplified folder structure: `infrastructure/`, `app/core/`, `data/`, `alembic/`, `tests/`, `bruno/`, and `.vscode/`.
- [x] 1.2 Add Python dependency declarations for FastAPI, Uvicorn, SQLAlchemy, PostgreSQL driver, Alembic, Pydantic settings or dotenv, multipart uploads, pytest, and HTTP test client support.
- [x] 1.3 Add `.env.example` with `DATABASE_URL` and basic app settings.
- [x] 1.4 Add `infrastructure/main.py` with a `create_app()` function, router registration, and Swagger UI enabled.

## 2. Configuration, Logging, And Debugging

- [x] 2.1 Add `infrastructure/settings/settings.py` for simple environment-based settings.
- [x] 2.2 Add `infrastructure/configuration/db_config.py` with SQLAlchemy engine, session factory, and `get_db` dependency.
- [x] 2.3 Add `infrastructure/configuration/log_config.py` with request ID context, console formatter, and `X-Request-ID` middleware.
- [x] 2.4 Add `infrastructure/configuration/middleware.py` to register request ID logging middleware.
- [x] 2.5 Add `.vscode/launch.json` following the core service uvicorn debug style for `infrastructure.main:app` on port `8000`.

## 3. Database, Alembic, And Transactions

- [x] 3.1 Add `data/model/transaction_model.py` with PostgreSQL-compatible columns for transaction data.
- [x] 3.2 Store `price` as a floating-point column.
- [x] 3.3 Store `date` as a database date while accepting and returning `DD-MM-YYYY` through the API.
- [x] 3.4 Configure Alembic to read `DATABASE_URL` and import model metadata.
- [x] 3.5 Add the initial Alembic migration for the transaction table.
- [x] 3.6 Implement explicit commit-on-success and rollback-on-failure handling for write operations.
- [x] 3.7 Verify `alembic upgrade head` creates the transaction table in PostgreSQL.

## 4. API Structure

- [x] 4.1 Add `infrastructure/routes/api_router.py` to include transaction and analytics controllers.
- [x] 4.2 Add `infrastructure/routes/controller/transaction_controller.py` with `POST /transactions`, `POST /transactions/bulk`, `POST /transactions/upload-csv`, and `GET /transactions`.
- [x] 4.3 Add `infrastructure/routes/controller/analytics_controller.py` with `GET /analytics/total-sales` and `GET /analytics/top-properties`.
- [x] 4.4 Keep controllers thin and delegate work to services.

## 5. Transactions And Ingestion

- [x] 5.1 Add transaction request/response schemas under `app/core/schema/`.
- [x] 5.2 Add `DD-MM-YYYY` date parsing and serialization helpers.
- [x] 5.3 Add transaction service logic under `app/core/service/` for validation orchestration, filtering, JSON bulk summaries, and CSV parsing.
- [x] 5.4 Add repository functions under `data/repository/` for create, bulk create, list with filters, total sales, and top properties.
- [x] 5.5 Store valid JSON bulk records and report invalid entries.
- [x] 5.6 Store valid CSV rows and report invalid rows.

## 6. Analytics

- [x] 6.1 Implement global total sales from all persisted transactions.
- [x] 6.2 Implement global top three properties by revenue.
- [x] 6.3 Use deterministic ordering for top properties when revenues tie.

## 7. Docker Runtime

- [x] 7.1 Add a Dockerfile that builds with `docker build -t fastapi-app .`.
- [x] 7.2 Add `docker-compose.yml` with API and PostgreSQL services.
- [x] 7.3 Add a named PostgreSQL Docker volume.
- [x] 7.4 Ensure the API container runs Alembic migrations before starting Uvicorn, or document the migration command clearly.

## 8. Bruno Manual Verification

- [x] 8.1 Add `bruno/hospitality-analytics-platform/bruno.json`.
- [x] 8.2 Add `bruno/hospitality-analytics-platform/environments/Local.bru` and `Local.json` with `baseUrl`, `category`, `startDate`, `endDate`, and reusable sample values.
- [x] 8.3 Add Transactions Bruno requests for valid create, missing field, invalid price, invalid date, list all, category filter, start-date filter, end-date filter, date-range filter, and combined filters.
- [x] 8.4 Add Bulk Upload Bruno requests for all-valid JSON bulk, mixed valid/invalid JSON bulk, and all-invalid JSON bulk.
- [x] 8.5 Add CSV Upload Bruno requests for valid CSV, mixed valid/invalid CSV, and missing-header CSV.
- [x] 8.6 Add Analytics Bruno requests for total sales and top properties.
- [x] 8.7 Add simple Bruno post-response scripts for status checks and useful variable capture, such as created transaction id.
- [x] 8.8 Add any small CSV fixture files needed by Bruno upload requests.

## 9. Unit Tests And AI Verification

- [x] 9.1 Add unit tests for single transaction creation and validation failures.
- [x] 9.2 Add unit tests for `DD-MM-YYYY` date parsing, response serialization, and invalid dates.
- [x] 9.3 Add unit tests for transaction listing, category filtering, date filtering, and combined filters.
- [x] 9.4 Add unit tests for JSON bulk partial-success behavior.
- [x] 9.5 Add unit tests for CSV upload partial-success behavior.
- [x] 9.6 Add unit tests for total sales and top properties analytics.
- [x] 9.7 Add unit tests for commit-on-success and rollback-on-failure database behavior.
- [x] 9.8 Run the unit test command after implementation and report the result.

## 10. Documentation

- [x] 10.1 Add README instructions for local setup, Docker Compose, Alembic migrations, Swagger UI, Bruno collection usage, and CSV format.
- [x] 10.2 Document that dates use `DD-MM-YYYY` in API payloads and filters.
- [x] 10.3 Document that `price` uses floating-point values for this assignment.
- [x] 10.4 Confirm JWT auth, RBAC, route interceptors, and other core-service enterprise layers were not added.
