from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.database.database import get_db
from app.dependencies.auth import get_current_user
from modules.utilisateurs.models import Utilisateur
from modules.signets.schemas import SignetCreate, SignetUpdate, SignetResponse, SignetListResponse
from modules.signets import service

router = APIRouter(prefix="/signets", tags=["Signets"])

@router.post("/", response_model=SignetResponse, status_code=status.HTTP_201_CREATED)
def creer_signet(
    data: SignetCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.creer_signet(db, current_user.id, data)

@router.get("/", response_model=SignetListResponse)
def mes_signets(
    livre_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.obtenir_mes_signets(db, current_user.id, livre_id)

@router.patch("/{signet_id}", response_model=SignetResponse)
def modifier_signet(
    signet_id: UUID,
    data: SignetUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.modifier_signet(db, signet_id, current_user.id, data)

@router.delete("/{signet_id}", status_code=status.HTTP_200_OK)
def supprimer_signet(
    signet_id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.supprimer_signet(db, signet_id, current_user.id)