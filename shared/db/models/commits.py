from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class CommitModel(Base):
    __tablename__ = 'commits'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey('repositories.id', ondelete='CASCADE'), nullable=False, index=True)
    sha = Column(String(40), nullable=False, index=True)
    author_email = Column(String(255), nullable=True)
    message = Column(String(1024), nullable=True)
    authored_at = Column(DateTime(timezone=True), nullable=False)
    files_changed = Column(JSONB, nullable=True) # E.g. {"added": [...], "modified": [...]}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
