from fastapi import APIRouter, Body, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schema.transaction_schema import (
    BulkCSVTransactionResponse,
    BulkTransactionResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionsResponsePaginated,
)
from app.core.service import transaction_service
from infrastructure.configuration.db_config import get_db

router = APIRouter(tags=["Transactions"])


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_transaction(payload: TransactionCreate, db: AsyncSession = Depends(get_db)):
    return await transaction_service.create_transaction(db, payload)


@router.post("/transactions/bulk", 
    response_model=BulkTransactionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_bulk_transactions(
    payload: list[TransactionCreate] = Body(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    return await transaction_service.create_bulk_transactions(db, payload)


@router.post("/transactions/upload-csv", 
    response_model=BulkCSVTransactionResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_csv_transactions(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await transaction_service.create_transactions_from_csv(db, file)


@router.get("/transactions", response_model=TransactionsResponsePaginated)
async def list_transactions(
    category: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await transaction_service.list_transactions(
        db,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )
