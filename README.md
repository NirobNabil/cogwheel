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
