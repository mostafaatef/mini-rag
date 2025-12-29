from sqlalchemy import Column, Integer, String, DateTime
from .mini_rag_base import SqlAlchemyBase
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import func
from sqlalchemy.orm import relationship

from .mixin import DictMixin


class Project(SqlAlchemyBase, DictMixin):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    assets = relationship(
        "Asset", back_populates="asset_project", cascade="all, delete-orphan"
    )
    chunks = relationship(
        "Chunk", back_populates="chunk_project", cascade="all, delete-orphan"
    )

    @property
    def project_title(self):
        return self.title

    def __repr__(self):
        return f"Project(uuid={self.uuid}, title={self.title}, description={self.description})"
