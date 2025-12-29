from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from .mini_rag_base import SqlAlchemyBase
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy.orm import relationship
from .project import Project
from .asset import Asset


from .mixin import DictMixin


class Chunk(SqlAlchemyBase, DictMixin):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    chunk_project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    chunk_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    chunk_content = Column(String, nullable=False)
    chunk_metadata = Column(JSON)
    chunk_order = Column(Integer, nullable=False)

    __table_args__ = (
        Index("idx_chunk_project_id", chunk_project_id),
        Index("idx_chunk_asset_id", chunk_asset_id),
    )

    chunk_project = relationship("Project", back_populates="chunks")
    chunk_asset = relationship("Asset", back_populates="chunks")

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"Chunk(uuid={self.uuid}, order={self.chunk_order})"
