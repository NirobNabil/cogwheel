from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


def transaction_payload(**overrides):
    payload = {
        "property_name": "Commit Hotel",
        "category": "rooms",
        "price": 100.0,
        "quantity": 1,
        "date": "01-04-2026",
    }
    payload.update(overrides)
    return payload


def force_commit_failure(monkeypatch):
    async def fail_commit(self):
        raise SQLAlchemyError("forced commit failure")

    monkeypatch.setattr(AsyncSession, "commit", fail_commit)


def test_successful_single_create_persists_record(client, count_transactions):
    response = client.post("/transactions", json=transaction_payload())

    assert response.status_code == 201
    assert count_transactions() == 1


def test_single_create_does_not_persist_record_when_database_write_fails(
    client,
    count_transactions,
    monkeypatch,
):
    force_commit_failure(monkeypatch)

    response = client.post("/transactions", json=transaction_payload())

    assert response.status_code == 500
    assert response.json()["detail"] == "Database write failed"
    assert count_transactions() == 0


def test_successful_bulk_create_persists_all_records(client, count_transactions):
    response = client.post(
        "/transactions/bulk",
        json=[
            transaction_payload(property_name="Bulk Commit One"),
            transaction_payload(property_name="Bulk Commit Two", date="02-04-2026"),
        ],
    )

    assert response.status_code == 201
    assert response.json() == {"inserted_count": 2}
    assert count_transactions() == 2


def test_bulk_create_does_not_persist_records_when_database_write_fails(
    client,
    count_transactions,
    monkeypatch,
):
    force_commit_failure(monkeypatch)

    response = client.post(
        "/transactions/bulk",
        json=[
            transaction_payload(property_name="Bulk Rollback One"),
            transaction_payload(property_name="Bulk Rollback Two", date="02-04-2026"),
        ],
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Database write failed for a batch of records"
    assert count_transactions() == 0


def test_csv_upload_does_not_persist_rows_when_database_write_fails(
    client,
    count_transactions,
    monkeypatch,
):
    force_commit_failure(monkeypatch)
    csv_body = "\n".join(
        [
            "property_name,category,price,quantity,date",
            "CSV Rollback One,rooms,100,1,01-04-2026",
            "CSV Rollback Two,food,200,1,02-04-2026",
        ]
    )

    response = client.post(
        "/transactions/upload-csv",
        files={"file": ("rollback.csv", csv_body, "text/csv")},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to process CSV file"
    assert count_transactions() == 0


def test_read_endpoints_do_not_change_data(client, count_transactions):
    response = client.post("/transactions", json=transaction_payload())
    assert response.status_code == 201
    before_count = count_transactions()

    transactions = client.get("/transactions")
    total_sales = client.get("/analytics/total-sales")

    assert transactions.status_code == 200
    assert total_sales.status_code == 200
    assert count_transactions() == before_count


def test_transactions_include_audit_columns(client, get_transactions):
    response = client.post("/transactions", json=transaction_payload())

    assert response.status_code == 201
    stored = get_transactions()[0]
    assert stored.created_at is not None
    assert stored.updated_at is None
