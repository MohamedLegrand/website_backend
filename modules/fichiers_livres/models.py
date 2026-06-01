import uuid
from sqlalchemy import String, ForeignKey, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class FichierLivre(Base):
    __tablename__ = "fichiers_livres"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    livre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("livres.id", ondelete="CASCADE"),
        nullable=False
    )
    format: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )
    chemin_fichier: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )
    fournisseur_stockage: Mapped[str | None] = mapped_column(String(50))
    taille_octets: Mapped[int | None] = mapped_column(BigInteger)
    televerse_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relations
    livre: Mapped["Livre"] = relationship("Livre", back_populates="fichiers")