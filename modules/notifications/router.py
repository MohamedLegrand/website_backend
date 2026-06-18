from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user
from modules.utilisateurs.models import Utilisateur
from modules.notifications.schemas import NotificationResponse, NotificationListResponse
from modules.notifications import service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=NotificationListResponse)
def mes_notifications(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return service.obtenir_mes_notifications(db, current_user.id)


@router.patch("/lire-tout", status_code=status.HTTP_200_OK)
def marquer_tout_comme_lu(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return service.marquer_tout_comme_lu(db, current_user.id)


@router.patch("/{notification_id}/lire", response_model=NotificationResponse)
def marquer_comme_lu(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return service.marquer_comme_lu(db, notification_id, current_user.id)


@router.delete("/", status_code=status.HTTP_200_OK)
def supprimer_toutes_notifications(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return service.supprimer_toutes_notifications(db, current_user.id)


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
def supprimer_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return service.supprimer_notification(db, notification_id, current_user.id)
