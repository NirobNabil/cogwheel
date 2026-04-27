FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
COPY data ./data
COPY infrastructure ./infrastructure

EXPOSE 8000

CMD ["sh", "-c", "uvicorn infrastructure.main:app --host 0.0.0.0 --port 8000"]
