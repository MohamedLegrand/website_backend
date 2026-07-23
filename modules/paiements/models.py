import uuid
from sqlalchemy import String, ForeignKey, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Paiement(Base):
    __tablename__ = "paiements"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    commande_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("commandes.id", ondelete="RESTRICT"),
        nullable=False
    )
    fournisseur: Mapped[str | None] = mapped_column(String(50))
    fournisseur_paiement_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    statut: Mapped[str] = mapped_column(String(20), default="en_attente")
    montant: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    devise: Mapped[str] = mapped_column(String(10), default="XAF")
    metadonnees: Mapped[dict | None] = mapped_column(JSON)
    paye_le: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    cree_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relations
    commande: Mapped["Commande"] = relationship("Commande", back_populates="paiement")