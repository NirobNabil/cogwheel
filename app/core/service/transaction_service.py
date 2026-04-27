import csv
from io import TextIOWrapper
import logging

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schema.transaction_schema import (
    BulkCSVTransactionResponse,
    BulkTransactionResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionsResponsePaginated,
    parse_transaction_date,
)
from data.repository import transaction_repository


async def create_transaction(db: AsyncSession, payload: TransactionCreate):
    try:
        data = await transaction_repository.create_transaction(db, payload)
        return TransactionResponse.model_validate(data)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database write failed",
        ) from exc


async def create_bulk_transactions(
    db: AsyncSession,
    items: list[TransactionCreate],
) -> BulkTransactionResponse:

    created_count = await transaction_repository.create_transactions(db, items)

    return BulkTransactionResponse(
        inserted_count=created_count,
    )


async def create_transactions_from_csv(db: AsyncSession, file: UploadFile) -> BulkCSVTransactionResponse:
    
    try:
        reader = csv.DictReader(
            TextIOWrapper(file.file, encoding="utf-8-sig")
        )
    except csv.Error as exc:
        logging.error("Failed to parse CSV file", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV file: {str(exc)}",
        ) from exc

    created_count, errors = await transaction_repository.create_transactions_from_csv(db, reader)        

    if created_count == 0 and errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Failed to ingest any records from the CSV file",
        )

    return BulkCSVTransactionResponse(
        inserted_count=created_count,
        failed_count=len(errors),
        errors=errors,
    )


async def list_transactions(
    db: AsyncSession,
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    page_size: int = 50
) -> TransactionsResponsePaginated:
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
    transactions, total = await transaction_repository.list_transactions(
        db,
        category=normalized_category,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        page=page,
        page_size=page_size
    )
    return TransactionsResponsePaginated(
        transactions=[
            TransactionResponse.model_validate(transaction)
            for transaction in transactions
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
