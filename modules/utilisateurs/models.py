import uuid
from sqlalchemy import String, Boolean, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database.base import Base
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    utilisateur = "utilisateur"

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    mot_de_passe_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    prenom: Mapped[str | None] = mapped_column(String(100))
    nom: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum),
        default=RoleEnum.utilisateur
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    est_actif: Mapped[bool] = mapped_column(Boolean, default=True)
    cree_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    modifie_le: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    langue: Mapped[str] = mapped_column(String(10), default="fr", server_default="'fr'")
    notif_email: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    notif_commandes: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    notif_promotions: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    notif_newsletter: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")