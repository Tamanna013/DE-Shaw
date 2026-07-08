from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared.db.base import Base, generate_uuid

team_members = Table(
    'team_members', Base.metadata,
    Column('team_id', String(36), ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)

class TeamModel(Base):
    __tablename__ = 'teams'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Assuming user_profiles is handled in user_management microservice for RBAC info,
    # but the users table is in shared DB. We link team_members to users here.
    members = relationship("UserModel", secondary=team_members)

class UserProfileModel(Base):
    __tablename__ = 'user_profiles'

    id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    team_id = Column(String(36), ForeignKey('teams.id', ondelete='SET NULL'), nullable=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
