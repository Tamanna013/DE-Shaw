from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class FlakyTestSignalModel(Base):
    __tablename__ = 'flaky_test_signals'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_case_id = Column(String(36), ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False, index=True)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    pass_count = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)
    flip_rate = Column(Float, nullable=False, default=0.0)
    confidence_score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
