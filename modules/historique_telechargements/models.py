import uuid
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class HistoriqueTelechargement(Base):
    __tablename__ = "historique_telechargements"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    utilisateur_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False
    )
    livre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("livres.id", ondelete="CASCADE"), nullable=False
    )
    fichier_livre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("fichiers_livres.id", ondelete="CASCADE"), nullable=False
    )
    format: Mapped[str] = mapped_column(String(10), nullable=False)
    adresse_ip: Mapped[str | None] = mapped_column(String(45))
    appareil: Mapped[str | None] = mapped_column(String(50))
    systeme_exploitation: Mapped[str | None] = mapped_column(String(50))
    telecharge_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur")
    livre: Mapped["Livre"] = relationship("Livre")
    fichier_livre: Mapped["FichierLivre"] = relationship("FichierLivre")