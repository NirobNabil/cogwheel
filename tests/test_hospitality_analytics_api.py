import inspect

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schema.transaction_schema import parse_transaction_date


def transaction_payload(**overrides):
    payload = {
        "property_name": "Harbor Hotel",
        "category": "rooms",
        "price": 120.5,
        "quantity": 2,
        "date": "01-04-2026",
    }
    payload.update(overrides)
    return payload


def create_transaction(client, **overrides):
    response = client.post("/transactions", json=transaction_payload(**overrides))
    assert response.status_code == 201, response.text
    return response.json()


def assert_listed_names(response, expected_names):
    assert response.status_code == 200, response.text
    assert [item["property_name"] for item in response.json()] == expected_names


CSV_COLUMNS = ["property_name", "category", "price", "quantity", "date"]


def csv_row(index, **overrides):
    row = {
        "property_name": f"CSV Row {index:04d}",
        "category": "rooms",
        "price": "10.5",
        "quantity": "1",
        "date": f"{((index - 1) % 28) + 1:02d}-04-2026",
    }
    row.update(overrides)
    return row


def csv_body(rows):
    lines = [",".join(CSV_COLUMNS)]
    for row in rows:
        lines.append(",".join(str(row[column]) for column in CSV_COLUMNS))
    return "\n".join(lines)


def test_application_route_handlers_are_async(client):
    application_paths = {
        "/health",
        "/transactions",
        "/transactions/bulk",
        "/transactions/upload-csv",
        "/analytics/total-sales",
        "/analytics/top-properties",
    }
    endpoints = {
        route.path: route.endpoint
        for route in client.app.routes
        if getattr(route, "path", None) in application_paths
    }

    assert set(endpoints) == application_paths
    assert all(inspect.iscoroutinefunction(endpoint) for endpoint in endpoints.values())


def test_health_check_echoes_or_generates_request_id(client):
    response = client.get("/health", headers={"X-Request-ID": "unit-test-request"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"] == "unit-test-request"

    generated = client.get("/health")
    assert generated.status_code == 200
    assert generated.headers["X-Request-ID"]


def test_single_transaction_creation_and_validation_failures(client, count_transactions):
    created = create_transaction(client)

    assert created == {
        "id": 1,
        "property_name": "Harbor Hotel",
        "category": "rooms",
        "price": 120.5,
        "quantity": 2,
        "date": "01-04-2026",
    }
    assert count_transactions() == 1

    invalid_payloads = [
        ({key: value for key, value in transaction_payload().items() if key != "property_name"}, "missing field"),
        (transaction_payload(price=0), "invalid price"),
        (transaction_payload(quantity=0), "invalid quantity"),
        (transaction_payload(category="   "), "empty category"),
    ]
    for payload, case_name in invalid_payloads:
        response = client.post("/transactions", json=payload)
        assert response.status_code == 422, case_name

    assert count_transactions() == 1


def test_dd_mm_yyyy_dates_are_parsed_serialized_and_validated(client, count_transactions):
    parsed = parse_transaction_date("09-04-2026")
    assert (parsed.day, parsed.month, parsed.year) == (9, 4, 2026)

    created = create_transaction(client, date="09-04-2026")
    assert created["date"] == "09-04-2026"

    listed = client.get("/transactions")
    assert_listed_names(listed, ["Harbor Hotel"])
    assert listed.json()[0]["date"] == "09-04-2026"

    for invalid_date in ["2026-04-09", "31-02-2026"]:
        response = client.post(
            "/transactions",
            json=transaction_payload(date=invalid_date),
        )
        assert response.status_code == 422

    invalid_filter = client.get("/transactions", params={"start_date": "2026-04-01"})
    assert invalid_filter.status_code == 422

    reversed_range = client.get(
        "/transactions",
        params={"start_date": "10-04-2026", "end_date": "01-04-2026"},
    )
    assert reversed_range.status_code == 422
    assert count_transactions() == 1


def test_transaction_listing_filters_and_pagination(client):
    create_transaction(client, property_name="Alpha", category="rooms", date="05-04-2026")
    create_transaction(client, property_name="Beta", category="food", date="01-04-2026")
    create_transaction(client, property_name="Gamma", category="rooms", date="10-04-2026")
    create_transaction(client, property_name="Delta", category="rooms", date="15-04-2026")

    assert_listed_names(client.get("/transactions"), ["Beta", "Alpha", "Gamma", "Delta"])
    assert_listed_names(client.get("/transactions", params={"category": "rooms"}), ["Alpha", "Gamma", "Delta"])
    assert_listed_names(client.get("/transactions", params={"start_date": "10-04-2026"}), ["Gamma", "Delta"])
    assert_listed_names(client.get("/transactions", params={"end_date": "05-04-2026"}), ["Beta", "Alpha"])
    assert_listed_names(
        client.get(
            "/transactions",
            params={
                "category": "rooms",
                "start_date": "05-04-2026",
                "end_date": "10-04-2026",
            },
        ),
        ["Alpha", "Gamma"],
    )
    assert_listed_names(client.get("/transactions", params={"category": "spa"}), [])
    assert_listed_names(client.get("/transactions", params={"page": 2, "page_size": 2}), ["Gamma", "Delta"])
    assert_listed_names(client.get("/transactions", params={"page": 3, "page_size": 2}), [])

    invalid_page = client.get("/transactions", params={"page": 0})
    invalid_page_size = client.get("/transactions", params={"page_size": 501})
    assert invalid_page.status_code == 422
    assert invalid_page_size.status_code == 422


def test_json_bulk_inserts_valid_batch_and_rejects_invalid_batches(client, count_transactions, get_transactions):
    response = client.post(
        "/transactions/bulk",
        json=[
            transaction_payload(property_name="Bulk Alpha", date="01-04-2026"),
            transaction_payload(property_name="Bulk Beta", date="02-04-2026"),
        ],
    )

    assert response.status_code == 201, response.text
    assert response.json() == {"inserted_count": 2}
    assert [record.property_name for record in get_transactions()] == ["Bulk Alpha", "Bulk Beta"]

    mixed_invalid = client.post(
        "/transactions/bulk",
        json=[
            transaction_payload(property_name="Bulk Gamma", date="03-04-2026"),
            transaction_payload(property_name="Bulk Invalid Price", price=-1),
        ],
    )
    empty_batch = client.post("/transactions/bulk", json=[])

    assert mixed_invalid.status_code == 422
    assert empty_batch.status_code == 422
    assert count_transactions() == 2


def test_csv_upload_reports_partial_success_and_rejects_bad_files(client, count_transactions, get_transactions):
    csv_body = "\n".join(
        [
            "property_name,category,price,quantity,date",
            "CSV Alpha,rooms,100.5,2,01-04-2026",
            "CSV Invalid,rooms,0,2,02-04-2026",
            "CSV Beta,food,75,3,03-04-2026",
            "CSV Bad Date,food,30,1,2026-04-04",
        ]
    )
    response = client.post(
        "/transactions/upload-csv",
        files={"file": ("transactions.csv", csv_body, "text/csv")},
    )

    assert response.status_code == 201, response.text
    assert response.json() == {
        "inserted_count": 2,
        "failed_count": 2,
        "errors": [
            {"row": 3, "errors": ["price: Value error, price must be greater than zero"]},
            {"row": 5, "errors": ["date: Value error, date must be in the format DD-MM-YYYY"]},
        ],
    }
    assert [record.property_name for record in get_transactions()] == ["CSV Alpha", "CSV Beta"]

    missing_headers = "property_name,category,price,date\nMissing,rooms,10,01-04-2026\n"
    rejected_headers = client.post(
        "/transactions/upload-csv",
        files={"file": ("missing.csv", missing_headers, "text/csv")},
    )
    assert rejected_headers.status_code == 422
    assert rejected_headers.json()["detail"]["missing_headers"] == ["quantity"]

    all_invalid = "property_name,category,price,quantity,date\nNope,rooms,0,1,01-04-2026\n"
    rejected_rows = client.post(
        "/transactions/upload-csv",
        files={"file": ("invalid.csv", all_invalid, "text/csv")},
    )
    assert rejected_rows.status_code == 422
    assert rejected_rows.json()["detail"] == "Failed to ingest any records from the CSV file"
    assert count_transactions() == 2


def test_csv_upload_batches_large_file_in_one_database_transaction(
    client,
    count_transactions,
    get_transactions,
    monkeypatch,
):
    original_commit = AsyncSession.commit
    commit_calls = 0

    async def counted_commit(self):
        nonlocal commit_calls
        commit_calls += 1
        await original_commit(self)

    monkeypatch.setattr(AsyncSession, "commit", counted_commit)
    rows = [csv_row(index) for index in range(1, 4006)]

    response = client.post(
        "/transactions/upload-csv",
        files={"file": ("large.csv", csv_body(rows), "text/csv")},
    )

    assert response.status_code == 201, response.text
    assert response.json() == {
        "inserted_count": 4005,
        "failed_count": 0,
        "errors": [],
    }
    assert commit_calls == 1
    assert count_transactions() == 4005

    stored = get_transactions()
    assert [stored[index].property_name for index in [0, 1999, 2000, 3999, 4004]] == [
        "CSV Row 0001",
        "CSV Row 2000",
        "CSV Row 2001",
        "CSV Row 4000",
        "CSV Row 4005",
    ]


def test_csv_upload_batches_only_valid_rows_and_reports_original_error_rows(
    client,
    count_transactions,
    get_transactions,
):
    invalid_values = {
        3: {"price": "0"},
        2001: {"quantity": "0"},
        4002: {"date": "2026-04-01"},
        4005: {"category": "   "},
    }
    rows = [
        csv_row(index, **invalid_values.get(index, {}))
        for index in range(1, 4006)
    ]

    response = client.post(
        "/transactions/upload-csv",
        files={"file": ("large-with-errors.csv", csv_body(rows), "text/csv")},
    )

    assert response.status_code == 201, response.text
    assert response.json() == {
        "inserted_count": 4001,
        "failed_count": 4,
        "errors": [
            {"row": 4, "errors": ["price: Value error, price must be greater than zero"]},
            {"row": 2002, "errors": ["quantity: Value error, quantity must be greater than zero"]},
            {"row": 4003, "errors": ["date: Value error, date must be in the format DD-MM-YYYY"]},
            {"row": 4006, "errors": ["category: Value error, must not be an empty string"]},
        ],
    }
    assert count_transactions() == 4001

    stored_names = {record.property_name for record in get_transactions()}
    assert {
        "CSV Row 0001",
        "CSV Row 2000",
        "CSV Row 2002",
        "CSV Row 4001",
        "CSV Row 4004",
    } <= stored_names
    assert not {
        "CSV Row 0003",
        "CSV Row 2001",
        "CSV Row 4002",
        "CSV Row 4005",
    } & stored_names


def test_total_sales_and_top_properties_with_deterministic_ties(client):
    create_transaction(client, property_name="Alpha", category="rooms", price=100.0, quantity=2)
    create_transaction(client, property_name="Alpha", category="food", price=50.0, quantity=2)
    create_transaction(client, property_name="Beta", category="rooms", price=150.0, quantity=2)
    create_transaction(client, property_name="Gamma", category="spa", price=200.0, quantity=1)
    create_transaction(client, property_name="Delta", category="rooms", price=100.0, quantity=1)

    total_sales = client.get("/analytics/total-sales")
    assert total_sales.status_code == 200
    assert total_sales.json() == {"total_sales": pytest.approx(900.0)}

    top_properties = client.get("/analytics/top-properties")
    assert top_properties.status_code == 200
    assert top_properties.json()["properties"] == [
        {"property_name": "Alpha", "revenue": pytest.approx(300.0)},
        {"property_name": "Beta", "revenue": pytest.approx(300.0)},
        {"property_name": "Gamma", "revenue": pytest.approx(200.0)},
    ]


def test_empty_database_analytics(client):
    total_sales = client.get("/analytics/total-sales")
    top_properties = client.get("/analytics/top-properties")

    assert total_sales.status_code == 200
    assert total_sales.json() == {"total_sales": 0.0}
    assert top_properties.status_code == 200
    assert top_properties.json() == {"properties": []}
