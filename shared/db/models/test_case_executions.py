from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class TestCaseExecutionModel(Base):
    __tablename__ = 'test_case_executions'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_run_id = Column(String(36), ForeignKey('test_runs.id', ondelete='CASCADE'), nullable=False, index=True)
    test_case_id = Column(String(36), ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(50), nullable=False)
    duration_ms = Column(Integer, nullable=False, default=0)
    stack_trace_id = Column(String(36), nullable=True) # Could be FK to a deduplicated stack trace table
    retry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite index for flaky-detection queries
    __table_args__ = (
        Index('ix_test_case_executions_test_case_id_status_created_at', 'test_case_id', 'status', 'created_at'),
    )
