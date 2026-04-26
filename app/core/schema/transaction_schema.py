import re
import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

DATE_FORMAT = "%d-%m-%Y"


def parse_transaction_date(value: Any) -> datetime.date:
    
    if isinstance(value, str):
        try:
            return datetime.datetime.strptime(value, "%d-%m-%Y").date()
        except ValueError:
            raise ValueError("date must be in the format DD-MM-YYYY")
    
    raise ValueError("date must be a string in the format DD-MM-YYYY")


def format_transaction_date(value: datetime.date) -> str:
    return value.strftime(DATE_FORMAT)


class TransactionCreate(BaseModel):
    property_name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float
    quantity: int
    date: datetime.date

    @field_validator("property_name", "category", mode="before")
    @classmethod
    def normalize_required_text(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("must be a string")
        normalized = value.strip()
        if not normalized:
            raise ValueError("must not be an empty string")
        return normalized

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("price must be greater than zero")
        return value

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("quantity must be greater than zero")
        return value

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, value: Any) -> datetime.date:
        return parse_transaction_date(value)


class TransactionResponse(BaseModel):
    id: int
    property_name: str
    category: str
    price: float
    quantity: int
    date: datetime.date

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("date")
    def serialize_date(self, value: datetime.date) -> str:
        return format_transaction_date(value)


class IngestionError(BaseModel):
    index: int | None = None
    row: int | None = None
    errors: list[str]


class BulkTransactionResponse(BaseModel):
    inserted_count: int
    failed_count: int
    created: list[TransactionResponse]
    errors: list[IngestionError]
