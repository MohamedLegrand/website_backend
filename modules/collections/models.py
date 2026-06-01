import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    nom: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)
    collection_parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("collections.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relations
    parent: Mapped["Collection | None"] = relationship(
        "Collection",
        remote_side="Collection.id",
        back_populates="sous_collections"
    )
    sous_collections: Mapped[list["Collection"]] = relationship(
        "Collection",
        back_populates="parent"
    )