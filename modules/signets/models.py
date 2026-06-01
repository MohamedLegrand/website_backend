import uuid
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Signet(Base):
    __tablename__ = "signets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    utilisateur_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False
    )
    livre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("livres.id", ondelete="CASCADE"), nullable=False
    )
    format: Mapped[str] = mapped_column(String(10), nullable=False)
    numero_page: Mapped[int | None] = mapped_column(Integer)
    position_epub_cfi: Mapped[str | None] = mapped_column(String(500))
    note: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur")
    livre: Mapped["Livre"] = relationship("Livre")