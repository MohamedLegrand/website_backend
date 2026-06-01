import uuid
from sqlalchemy import Text, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Avis(Base):
    __tablename__ = "avis"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    utilisateur_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False
    )
    livre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("livres.id", ondelete="CASCADE"), nullable=False
    )
    note: Mapped[int] = mapped_column(Integer, nullable=False)
    commentaire: Mapped[str | None] = mapped_column(Text)
    est_approuve: Mapped[bool] = mapped_column(Boolean, default=False)
    cree_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur")
    livre: Mapped["Livre"] = relationship("Livre")