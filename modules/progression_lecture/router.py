from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user
from modules.utilisateurs.models import Utilisateur
from modules.progression_lecture.schemas import (
    ProgressionCreate,
    ProgressionResponse,
    ProgressionListResponse
)
from modules.progression_lecture import service

router = APIRouter(prefix="/progression-lecture", tags=["Progression Lecture"])

@router.post("/", response_model=ProgressionResponse, status_code=status.HTTP_200_OK)
def sauvegarder_progression(
    data: ProgressionCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.creer_ou_mettre_a_jour(db, current_user.id, data)

@router.get("/", response_model=ProgressionListResponse)
def mes_progressions(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.obtenir_mes_progressions(db, current_user.id)

@router.get("/{livre_id}", response_model=ProgressionResponse)
def progression_livre(
    livre_id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.obtenir_progression_livre(db, current_user.id, livre_id)

@router.delete("/{livre_id}", status_code=status.HTTP_200_OK)
def supprimer_progression(
    livre_id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.supprimer_progression(db, current_user.id, livre_id)