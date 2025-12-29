from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from .mini_rag_base import SqlAlchemyBase
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy import Index


from .mixin import DictMixin


class Asset(SqlAlchemyBase, DictMixin):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    asset_project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    asset_project = relationship("Project", back_populates="assets")
    chunks = relationship(
        "Chunk", back_populates="chunk_asset", cascade="all, delete-orphan"
    )

    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_size = Column(Integer)
    asset_path = Column(String)
    asset_metadata = Column(JSON)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_asset_project_id", asset_project_id),
        Index("idx_asset_name", asset_name),
    )

    def __repr__(self):
        return (
            f"Asset(uuid={self.uuid}, name={self.asset_name}, type={self.asset_type})"
        )
