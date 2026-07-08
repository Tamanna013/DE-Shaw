from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from shared.db.base import Base, generate_uuid

class FailureEmbeddingModel(Base):
    __tablename__ = 'failure_embeddings'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    # failure_id FK omitted here to avoid circular dependency / allow sharing, 
    # as failures points to embeddings.
    vector = Column(Vector(768), nullable=False)
    model_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Note: IVFFLAT index must be created via Alembic script using:
    # op.execute("CREATE INDEX ON failure_embeddings USING ivfflat (vector vector_cosine_ops) WITH (lists = 100);")
