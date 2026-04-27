from collections.abc import Callable
from csv import DictReader
import logging
from collections.abc import Sequence
from datetime import date

from fastapi import status, HTTPException
from pydantic_core import ValidationError
from sqlalchemy import Select, insert, desc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schema.transaction_schema import IngestionError, TransactionCreate
from app.core.schema.analytics_schema import TopPropertyRevenue
from app.core.service.transaction_service import _format_validation_errors
from data.model.transaction_model import Transaction, TransactionRet


########
# only handle sql or repository level errors in repository layer. service layer should handle rest
########

def _to_transaction_model(payload: TransactionCreate) -> Transaction:
    return Transaction(
        property_name=payload.property_name,
        category=payload.category,
        price=float(payload.price),
        quantity=payload.quantity,
        date=payload.date,
    )


async def create_transaction(db: AsyncSession, payload: TransactionCreate) -> TransactionRet:
    try:
        record = _to_transaction_model(payload)
    except Exception as e:
        # ideally code should never reach here since payload is already validated. 
        # so this exception means validation in service layer is faulty
        logging.error("Failed to convert payload to transaction model", exc_info=e)
        raise
    
    try:
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return TransactionRet.model_validate(record)
    except SQLAlchemyError:
        await db.rollback()
        raise

#TODO: need to optimize for memory usage and performance when inserting large number of records
async def create_transactions(
    db: AsyncSession,
    payloads: Sequence[TransactionCreate],
) -> int:
    _records = [] 
    
    try:
        for payload in payloads:
            transaction = _to_transaction_model(payload)
            _records.append({
                "property_name": transaction.property_name,
                "category": transaction.category,
                "price": transaction.price,
                "quantity": transaction.quantity,
                "date": transaction.date,
            })
    except Exception as e:
        # ideally code should never reach here since payloads are already validated. 
        # so this exception means validation in service layer is faulty
        logging.error("Failed to convert payloads to transaction models", exc_info=e)
        raise

    stmt = insert(Transaction).values(_records).returning(Transaction)
    
    try:
        rows = await db.execute(stmt)
        records = rows.scalars().all()
    
        return len(records)
    except SQLAlchemyError as e:
        logging.error("Failed to create transactions in db", exc_info=e)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database write failed for a batch of records",
        ) from e


REQUIRED_CSV_HEADERS = {"property_name", "category", "price", "quantity", "date"}

async def create_transactions_from_csv(
    db: AsyncSession,
    reader: DictReader,
    validation_error_formatter: Callable[[ValidationError], list[str]] = _format_validation_errors,
) -> tuple[int, list[IngestionError]]:

    # used for staging a batch of insert in the db transaction
    async def stage_data(payloads: list[TransactionCreate]) -> int:
        
        _records = []
        try:
            for payload in payloads:
                transaction = _to_transaction_model(payload)
                _records.append({
                    "property_name": transaction.property_name,
                    "category": transaction.category,
                    "price": transaction.price,
                    "quantity": transaction.quantity,
                    "date": transaction.date,
                })
        except Exception as e:
            logging.error("Failed to convert row into transaction models")
            raise

        try:
            stmt = insert(Transaction).values(_records).returning(Transaction)
            rows = await db.execute(stmt)
            records = rows.scalars().all()

            if len(records) != len(payloads):
                logging.error("Mismatch in number of records created and payloads staged")
                raise Exception("Database write failed for a batch of records")
        
            return len(records)
        except SQLAlchemyError as e:
            logging.error("Failed to create transactions in db")
            raise
    
    valid: list[TransactionCreate] = []
    errors: list[IngestionError] = []
    created_count: int = 0
    BATCH_SIZE = 2000
    
    headers = set(reader.fieldnames or [])
    missing_headers = sorted(REQUIRED_CSV_HEADERS - headers)
    if missing_headers:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "message": "CSV file is missing required headers",
                "missing_headers": missing_headers,
            },
        )
    
    try:
        for row_number, row in enumerate(reader, start=2):
            row_d = {header: row.get(header) for header in REQUIRED_CSV_HEADERS}
            try:
                valid.append(TransactionCreate.model_validate(row_d))
            except ValidationError as exc:
                errors.append(IngestionError(row=row_number, errors=validation_error_formatter(exc)))
        
            # batch size is 2000
            # it is guaranteed that created_count will be in sync with len(valid) because otherwise stage_data would through exception
            if len(valid) - created_count >= BATCH_SIZE:
                created_count += await stage_data(valid[created_count:created_count + BATCH_SIZE])

        if len(valid) != created_count:
            created_count += await stage_data(valid[created_count:])
        
        await db.commit()

    except Exception as exc:
        logging.error("Failed to process CSV file", exc_info=exc)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process CSV file",
        ) from exc
    

    return created_count, errors



async def list_transactions(
    db: AsyncSession,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[TransactionRet]:
    try:
        stmt = select(Transaction)
        if category:
            stmt = stmt.where(Transaction.category == category)
        if start_date:
            stmt = stmt.where(Transaction.date >= start_date)
        if end_date:
            stmt = stmt.where(Transaction.date <= end_date)
        stmt = stmt.order_by(Transaction.date.asc(), Transaction.id.asc())
        result = await db.execute(stmt)
        return [TransactionRet.model_validate(row) for row in result.scalars().all()]
    except SQLAlchemyError as exc:
        logging.error("Failed to fetch transactions from db", exc_info=exc)
        raise


async def total_sales(db: AsyncSession) -> float:
    try:
        revenue = func.coalesce(func.sum(Transaction.price * Transaction.quantity), 0.0)
        value = await db.scalar(select(revenue))
        return float(value or 0.0)
    except SQLAlchemyError as exc:
        logging.error("Failed to calculate total sales from db", exc_info=exc)
        raise


async def top_properties(db: AsyncSession, limit: int = 3) -> list[TopPropertyRevenue]:

    try:
        revenue = func.coalesce(func.sum(Transaction.price * Transaction.quantity), 0.0).label("revenue")
        stmt = (
            select(Transaction.property_name, revenue)
            .group_by(Transaction.property_name)
            .order_by(desc(revenue), Transaction.property_name.asc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.mappings().all()
        return [
            TopPropertyRevenue(
                property_name=row["property_name"],
                revenue=float(row["revenue"] or 0.0)
            )
            for row in rows
        ]
    except SQLAlchemyError as exc:
        logging.error("Failed to fetch top properties from db", exc_info=exc)
        raise
