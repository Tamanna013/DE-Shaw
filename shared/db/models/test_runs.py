from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class TestRunModel(Base):
    __tablename__ = 'test_runs'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey('repositories.id', ondelete='RESTRICT'), nullable=False, index=True)
    commit_sha = Column(String(40), nullable=False, index=True)
    branch = Column(String(255), nullable=False)
    trigger = Column(String(50), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, index=True)
    ci_provider = Column(String(100), nullable=False)
    ci_run_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
