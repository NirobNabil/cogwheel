from pydantic import BaseModel


class TotalSalesResponse(BaseModel):
    total_sales: float


class TopPropertyRevenue(BaseModel):
    property_name: str
    revenue: float


class TopPropertiesResponse(BaseModel):
    properties: list[TopPropertyRevenue]
