import uuid
from sqlalchemy import String, ForeignKey, Numeric, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Commande(Base):
    __tablename__ = "commandes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    utilisateur_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="RESTRICT"), nullable=False
    )
    statut: Mapped[str] = mapped_column(String(20), default="en_attente")
    montant_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    devise: Mapped[str] = mapped_column(String(10), default="EUR")
    cree_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    modifie_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur")
    lignes: Mapped[list["LigneCommande"]] = relationship(
        "LigneCommande",
        back_populates="commande",
        cascade="all, delete-orphan"
    )
    paiement: Mapped["Paiement | None"] = relationship(
        "Paiement",
        back_populates="commande",
        uselist=False
    )


class LigneCommande(Base):
    __tablename__ = "lignes_commandes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    commande_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("commandes.id", ondelete="CASCADE"), nullable=False
    )
    livre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("livres.id", ondelete="RESTRICT"), nullable=False
    )
    prix_unitaire: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantite: Mapped[int] = mapped_column(Integer, default=1)

    # Relations
    commande: Mapped["Commande"] = relationship("Commande", back_populates="lignes")
    livre: Mapped["Livre"] = relationship("Livre")