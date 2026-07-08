from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class CommitTestCorrelationModel(Base):
    __tablename__ = 'commit_test_correlations'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    commit_id = Column(String(36), ForeignKey('commits.id', ondelete='CASCADE'), nullable=False, index=True)
    test_case_id = Column(String(36), ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False, index=True)
    correlation_type = Column(String(50), nullable=False) # e.g. "file_modification", "historical_failure"
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
