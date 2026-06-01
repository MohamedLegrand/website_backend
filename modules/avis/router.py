from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.avis.schemas import AvisCreate, AvisResponse, AvisListResponse
from modules.avis import service

router = APIRouter(prefix="/avis", tags=["Avis"])

@router.post("/", response_model=AvisResponse, status_code=status.HTTP_201_CREATED)
def creer_avis(
    data: AvisCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.creer_avis(db, current_user.id, data)

@router.get("/livre/{livre_id}", response_model=AvisListResponse)
def avis_livre(
    livre_id: UUID,
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db)
):
    return service.obtenir_avis_livre(db, livre_id, page, taille)

@router.get("/", response_model=AvisListResponse)
def tous_les_avis(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.obtenir_tous_avis(db, page, taille)

@router.patch("/{avis_id}/approuver", response_model=AvisResponse)
def approuver_avis(
    avis_id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.approuver_avis(db, avis_id)

@router.delete("/{avis_id}", status_code=status.HTTP_200_OK)
def supprimer_avis(
    avis_id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.supprimer_avis(db, avis_id)