from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import TIMESTAMP


class AuditBaseModel:
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now(), nullable=True)
