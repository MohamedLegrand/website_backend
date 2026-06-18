import uuid
from sqlalchemy import ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Panier(Base):
    __tablename__ = "panier"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    utilisateur_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    cree_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    modifie_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relations — pas de back_populates vers Utilisateur
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur")
    lignes: Mapped[list["LignePanier"]] = relationship(
        "LignePanier",
        back_populates="panier",
        cascade="all, delete-orphan"
    )


class LignePanier(Base):
    __tablename__ = "lignes_panier"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    panier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("panier.id", ondelete="CASCADE"),
        nullable=False
    )
    livre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("livres.id", ondelete="CASCADE"),
        nullable=False
    )
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    ajoute_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relations
    panier: Mapped["Panier"] = relationship("Panier", back_populates="lignes")
    livre: Mapped["Livre"] = relationship("Livre")