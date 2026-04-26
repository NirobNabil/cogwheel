import csv
from collections.abc import Iterable
from io import TextIOWrapper
from typing import Any

from fastapi import HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schema.transaction_schema import (
    BulkTransactionResponse,
    IngestionError,
    TransactionCreate,
    parse_transaction_date,
)
from data.repository import transaction_repository

from app.core.schema.transaction_schema import TransactionResponse

REQUIRED_CSV_HEADERS = {"property_name", "category", "price", "quantity", "date"}


def _format_validation_errors(exc: ValidationError) -> list[str]:
    messages: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", []))
        message = error.get("msg", "Invalid value")
        messages.append(f"{location}: {message}" if location else message)
    return messages


def _validate_items(items: Iterable[dict[str, Any]]) -> tuple[list[TransactionCreate], list[IngestionError]]:
    valid: list[TransactionCreate] = []
    errors: list[IngestionError] = []
    for index, item in enumerate(items):
        try:
            valid.append(TransactionCreate.model_validate(item))
        except ValidationError as exc:
            errors.append(IngestionError(index=index, errors=_format_validation_errors(exc)))
    return valid, errors


async def create_transaction(db: AsyncSession, payload: TransactionCreate):
    try:
        return await transaction_repository.create_transaction(db, payload)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database write failed",
        ) from exc


async def create_bulk_transactions(
    db: AsyncSession,
    items: list[dict[str, Any]],
) -> BulkTransactionResponse:
    valid, errors = _validate_items(items)
    created = []
    if valid:
        try:
            created = await transaction_repository.create_transactions(db, valid)
        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database write failed",
            ) from exc

    return BulkTransactionResponse(
        inserted_count=len(created),
        failed_count=len(errors),
        created= [TransactionResponse.model_validate(record) for record in created],
        errors=errors,
    )


async def create_transactions_from_csv(db: AsyncSession, file: UploadFile) -> BulkTransactionResponse:
    reader = csv.DictReader(
        TextIOWrapper(file.file, encoding="utf-8-sig")
    )
    headers = set(reader.fieldnames or [])
    missing_headers = sorted(REQUIRED_CSV_HEADERS - headers)
    if missing_headers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "CSV file is missing required headers",
                "missing_headers": missing_headers,
            },
        )

    valid: list[TransactionCreate] = []
    errors: list[IngestionError] = []
    for row_number, row in enumerate(reader, start=2):
        payload = {header: row.get(header) for header in REQUIRED_CSV_HEADERS}
        try:
            valid.append(TransactionCreate.model_validate(payload))
        except ValidationError as exc:
            errors.append(IngestionError(row=row_number, errors=_format_validation_errors(exc)))

    created = []
    if valid:
        try:
            created = await transaction_repository.create_transactions(db, valid)
        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database write failed",
            ) from exc

    return BulkTransactionResponse(
        inserted_count=len(created),
        failed_count=len(errors),
        created=[TransactionResponse.model_validate(record) for record in created],
        errors=errors,
    )


async def list_transactions(
    db: AsyncSession,
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    try:
        parsed_start_date = parse_transaction_date(start_date) if start_date else None
        parsed_end_date = parse_transaction_date(end_date) if end_date else None
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    if parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="start_date must be on or before end_date",
        )

    normalized_category = category.strip() if category else None
    return await transaction_repository.list_transactions(
        db,
        category=normalized_category,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
    )
