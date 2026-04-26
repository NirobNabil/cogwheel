from collections.abc import Sequence
from datetime import date

from sqlalchemy import Select, insert, desc, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schema.transaction_schema import TransactionCreate
from app.core.schema.analytics_schema import TopPropertyRevenue
from data.model.transaction_model import Transaction, TransactionRet


def _to_transaction_model(payload: TransactionCreate) -> Transaction:
    return Transaction(
        property_name=payload.property_name,
        category=payload.category,
        price=float(payload.price),
        quantity=payload.quantity,
        date=payload.date,
    )


async def create_transaction(db: AsyncSession, payload: TransactionCreate) -> TransactionRet:
    record = _to_transaction_model(payload)
    db.add(record)
    try:
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
) -> list[TransactionRet]:
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
        raise

    stmt = insert(Transaction).values(_records).returning(Transaction)
    
    try:
        rows = await db.execute(stmt)
        records = rows.scalars().all()
    
        return [ TransactionRet.model_validate(record) for record in records ]
    except Exception as e:
        await db.rollback()
        raise


async def list_transactions(
    db: AsyncSession,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[TransactionRet]:
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


async def total_sales(db: AsyncSession) -> float:
    revenue = func.coalesce(func.sum(Transaction.price * Transaction.quantity), 0.0)
    value = await db.scalar(select(revenue))
    return float(value or 0.0)


async def top_properties(db: AsyncSession, limit: int = 3) -> list[TopPropertyRevenue]:
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
