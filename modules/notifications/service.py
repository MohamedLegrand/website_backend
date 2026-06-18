from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.notifications.models import Notification
from modules.notifications.schemas import NotificationCreate

def creer_notification(db: Session, data: NotificationCreate) -> Notification:
    notification = Notification(
        utilisateur_id=data.utilisateur_id,
        titre=data.titre,
        message=data.message,
        type=data.type,
        lien=data.lien
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def obtenir_mes_notifications(db: Session, utilisateur_id: UUID) -> dict:
    notifications = db.execute(
        select(Notification).where(
            Notification.utilisateur_id == utilisateur_id
        ).order_by(Notification.cree_le.desc())
    ).scalars().all()

    non_lues = db.execute(
        select(func.count(Notification.id)).where(
            Notification.utilisateur_id == utilisateur_id,
            Notification.est_lu == False
        )
    ).scalar()

    return {"total": len(notifications), "non_lues": non_lues, "notifications": notifications}

def marquer_comme_lu(db: Session, notification_id: UUID, utilisateur_id: UUID) -> Notification:
    notification = db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.utilisateur_id == utilisateur_id
        )
    ).scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification non trouvée")

    notification.est_lu = True
    db.commit()
    db.refresh(notification)
    return notification

def marquer_tout_comme_lu(db: Session, utilisateur_id: UUID) -> dict:
    notifications = db.execute(
        select(Notification).where(
            Notification.utilisateur_id == utilisateur_id,
            Notification.est_lu == False
        )
    ).scalars().all()

    for notification in notifications:
        notification.est_lu = True

    db.commit()
    return {"message": f"{len(notifications)} notification(s) marquée(s) comme lue(s)"}

def supprimer_notification(db: Session, notification_id: UUID, utilisateur_id: UUID) -> dict:
    notification = db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.utilisateur_id == utilisateur_id
        )
    ).scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification non trouvée")

    db.delete(notification)
    db.commit()
    return {"message": "Notification supprimée avec succès"}

def supprimer_toutes_notifications(db: Session, utilisateur_id: UUID) -> dict:
    notifications = db.execute(
        select(Notification).where(Notification.utilisateur_id == utilisateur_id)
    ).scalars().all()

    count = len(notifications)
    for n in notifications:
        db.delete(n)
    db.commit()
    return {"message": f"{count} notification(s) supprimée(s)"}