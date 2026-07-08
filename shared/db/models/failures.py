from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class FailureModel(Base):
    __tablename__ = 'failures'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_case_execution_id = Column(String(36), ForeignKey('test_case_executions.id', ondelete='CASCADE'), nullable=False, index=True)
    error_type = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    stack_trace_raw = Column(Text, nullable=True)
    normalized_signature = Column(Text, nullable=True, index=True)
    embedding_id = Column(String(36), ForeignKey('failure_embeddings.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
