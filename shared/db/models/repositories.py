from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class RepositoryModel(Base):
    __tablename__ = 'repositories'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    git_url = Column(String(1024), nullable=False)
    provider = Column(String(50), nullable=False)
    default_branch = Column(String(255), nullable=False, default="main")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
