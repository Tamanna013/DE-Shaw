from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

class TestCaseModel(Base):
    __tablename__ = 'test_cases'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey('repositories.id', ondelete='RESTRICT'), nullable=False, index=True)
    qualified_name = Column(String(1024), nullable=False)
    file_path = Column(String(1024), nullable=False)
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('repository_id', 'qualified_name', name='uq_test_cases_repository_id_qualified_name'),
    )
