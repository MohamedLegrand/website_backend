import uuid
from sqlalchemy import String, Text, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Livre(Base):
    __tablename__ = "livres"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    titre: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    auteur: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    couverture_url: Mapped[str | None] = mapped_column(String(500))
    quatrieme_couverture_url: Mapped[str | None] = mapped_column(String(500))
    sommaire_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String(500)))
    langue: Mapped[str | None] = mapped_column(String(50))
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True)
    prix: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    est_gratuit: Mapped[bool] = mapped_column(Boolean, default=False)
    est_publie: Mapped[bool] = mapped_column(Boolean, default=False)
    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("collections.id", ondelete="SET NULL"),
        nullable=True
    )
    publie_le: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    cree_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    modifie_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relations
    collection: Mapped["Collection | None"] = relationship("Collection")
    fichiers: Mapped[list["FichierLivre"]] = relationship(
        "FichierLivre",
        back_populates="livre",
        cascade="all, delete-orphan"
    )