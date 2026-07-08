from sqlalchemy import Column, String, DateTime, func
from shared.db.base import Base, generate_uuid

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BlockedEmailDomainModel(Base):
    __tablename__ = 'blocked_email_domains'
    domain = Column(String(255), primary_key=True)
