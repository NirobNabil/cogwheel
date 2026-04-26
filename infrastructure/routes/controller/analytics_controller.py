from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schema.analytics_schema import TotalSalesResponse, TopPropertiesResponse
from app.core.service import analytics_service
from infrastructure.configuration.db_config import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/total-sales", response_model=TotalSalesResponse)
async def total_sales(db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_total_sales(db)


@router.get("/top-properties", response_model=TopPropertiesResponse)
async def top_properties(db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_top_properties(db)
