from sqlalchemy.orm import Session
from uuid import UUID
from modules.notifications.models import Notification


def notifier(
    db: Session,
    utilisateur_id: UUID,
    titre: str,
    message: str,
    type_notif: str,
    lien: str | None = None,
) -> None:
    """Ajoute une notification à la session sans commit — le caller commit."""
    db.add(Notification(
        utilisateur_id=utilisateur_id,
        titre=titre,
        message=message,
        type=type_notif,
        lien=lien,
    ))
