from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class AuditLogModel(Base):
    __tablename__ = 'audit_log'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=False)
    target_id = Column(String(36), nullable=False, index=True)
    metadata_ = Column("metadata", JSONB, nullable=True) # avoiding reserved keyword conflict with metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
