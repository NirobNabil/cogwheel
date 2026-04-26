# Hospitality Analytics Platform

Lightweight FastAPI service for storing hospitality transactions, ingesting JSON or CSV batches, listing filtered transactions, and returning simple revenue analytics.

## Requirements

- Python 3.12 or compatible Python 3.x runtime
- PostgreSQL
- Docker and Docker Compose for the container workflow

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create local environment configuration:

```powershell
Copy-Item .env.example .env
```

Update `DATABASE_URL` in `.env` if your PostgreSQL credentials differ. The default local value is:

```text
postgresql+psycopg://hospitality:hospitality@localhost:5432/hospitality
```

The API uses SQLAlchemy async sessions for runtime database access. Keep the `postgresql+psycopg` URL format for PostgreSQL; Alembic uses the same value for migrations.

Apply database migrations before starting the app:

```powershell
alembic upgrade head
```

Run the API:

```powershell
uvicorn infrastructure.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI is available at `http://localhost:8000/docs`. The OpenAPI schema is available at `http://localhost:8000/openapi.json`.

## Docker Compose

Start PostgreSQL and the API together:

```powershell
docker compose up --build
```

The `api` service receives a Compose `DATABASE_URL` that points to the `postgres` service. It runs:

```text
alembic upgrade head && uvicorn infrastructure.main:app --host 0.0.0.0 --port 8000
```

PostgreSQL data is stored in the named Docker volume `hospitality_postgres_data`, so data persists when containers are recreated. Remove that volume only when you want to discard local database data.

Build only the API image with the assignment command:

```powershell
docker build -t fastapi-app .
```

If you run the image outside Compose, provide a valid PostgreSQL `DATABASE_URL`:

```powershell
docker run --rm -p 8000:8000 -e DATABASE_URL="postgresql+psycopg://hospitality:hospitality@host.docker.internal:5432/hospitality" fastapi-app
```

## Alembic Migrations

This project uses Alembic for schema management. The application does not create tables directly on startup.
Runtime database access is async, while Alembic migration commands run through SQLAlchemy's synchronous migration engine. The configured PostgreSQL URL works for both paths.

Run migrations manually in local development:

```powershell
alembic upgrade head
```

The Dockerfile and Docker Compose API command run migrations automatically before Uvicorn starts.

## API Notes

Transaction payloads use these fields:

```json
{
  "property_name": "Seaside Resort",
  "category": "rooms",
  "price": 125.5,
  "quantity": 2,
  "date": "01-04-2026"
}
```

Dates in API payloads, JSON bulk records, CSV rows, and `GET /transactions` filters use `DD-MM-YYYY`.

`price` uses floating-point values for this assignment. This keeps the implementation simple and is not intended as production-grade money precision.

Main endpoints:

- `POST /transactions`
- `POST /transactions/bulk`
- `POST /transactions/upload-csv`
- `GET /transactions`
- `GET /analytics/total-sales`
- `GET /analytics/top-properties`

## CSV Upload Format

Upload CSV files to `POST /transactions/upload-csv` using a multipart file field named `file`. Swagger UI exposes this as a file picker.

CSV files must include these headers:

```text
property_name,category,price,quantity,date
```

Example:

```csv
property_name,category,price,quantity,date
Seaside Resort,rooms,125.5,2,01-04-2026
City Hotel,food,18.75,4,02-04-2026
```

Rows must use positive floating-point `price` values, positive integer `quantity` values, and `DD-MM-YYYY` dates. Valid rows are stored and invalid rows are reported in the response.

## Bruno Collection

Open the Bruno collection at `bruno/hospitality-analytics-platform`, select the `Local` environment, and confirm `baseUrl` is `http://localhost:8000`.

Use the collection to run transaction creation/listing requests, JSON bulk ingestion requests, CSV upload requests, and analytics requests against a locally running API. The Local environment is expected to include reusable values such as `baseUrl`, `category`, `startDate`, and `endDate`.

## Deliberately Excluded

JWT authentication, RBAC, route interceptors, permission decorators, user account layers, scanners, gateways, Redis, Helm, Kubernetes manifests, and other enterprise layers from the reference core service were not added. The assignment service keeps routes public and focuses on transaction ingestion, persistence, analytics, migrations, Docker runtime, and manual verification.
