from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schema.analytics_schema import TotalSalesResponse, TopPropertiesResponse
from data.repository import transaction_repository


async def get_total_sales(db: AsyncSession) -> TotalSalesResponse:
    return TotalSalesResponse(total_sales=await transaction_repository.total_sales(db))


async def get_top_properties(db: AsyncSession) -> TopPropertiesResponse:
    return TopPropertiesResponse(properties=await transaction_repository.top_properties(db))
