import uuid
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class AccesLivre(Base):
    __tablename__ = "acces_livres"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    utilisateur_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False
    )
    livre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("livres.id", ondelete="CASCADE"), nullable=False
    )
    commande_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("commandes.id", ondelete="RESTRICT"), nullable=False
    )
    accorde_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expire_le: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur")
    livre: Mapped["Livre"] = relationship("Livre")
    commande: Mapped["Commande"] = relationship("Commande")