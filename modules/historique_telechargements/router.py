from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.historique_telechargements.schemas import HistoriqueListResponse
from modules.historique_telechargements import service

router = APIRouter(prefix="/historique-telechargements", tags=["Historique Téléchargements"])

@router.get("/mes-telechargements", response_model=HistoriqueListResponse)
def mon_historique(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.obtenir_mon_historique(db, current_user.id, page, taille)

@router.get("/", response_model=HistoriqueListResponse)
def tout_historique(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.obtenir_tout_historique(db, page, taille)