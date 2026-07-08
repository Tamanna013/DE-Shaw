from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class CommitTestCorrelationModel(Base):
    __tablename__ = 'commit_test_correlations'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_case_id = Column(String(36), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False, index=True)
    fails_caused = Column(Integer, default=0, nullable=False)
    historical_score_cached = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
