from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class FailureAnalysisReportModel(Base):
    __tablename__ = 'failure_analysis_reports'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_id = Column(String(36), nullable=False, unique=True, index=True)
    test_case_id = Column(String(36), nullable=False, index=True)
    analyzed_at = Column(DateTime(timezone=True), nullable=False)
    ai_reasoning_status = Column(String(50), nullable=False)
    hypotheses = Column(JSONB, nullable=False) # List of dicts
    flaky_signal_score = Column(Float, nullable=False, default=0.0)
    context_bundle_summary = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OutboxEventModel(Base):
    __tablename__ = 'outbox_events'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(255), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
