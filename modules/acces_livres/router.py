from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.acces_livres.schemas import AccesLivreResponse, AccesLivreListResponse
from modules.acces_livres import service

router = APIRouter(prefix="/acces-livres", tags=["Accès Livres"])

@router.get("/mes-acces", response_model=AccesLivreListResponse)
def mes_acces(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.obtenir_mes_acces(db, current_user.id, page, taille)

@router.get("/verifier/{livre_id}")
def verifier_acces(
    livre_id: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """livre_id accepte soit l'UUID en base, soit le slug"""
    acces = service.verifier_acces(db, current_user.id, livre_id)
    return {"a_acces": acces}

@router.get("/", response_model=AccesLivreListResponse)
def tous_les_acces(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.obtenir_tous_acces(db, page, taille)

@router.delete("/{acces_id}", status_code=status.HTTP_200_OK)
def revoquer_acces(
    acces_id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.revoquer_acces(db, acces_id)