from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user
from modules.utilisateurs.models import Utilisateur
from modules.panier.schemas import (
    AjouterLivreSchema,
    PanierResponse,
    PanierTotalResponse
)
from modules.commandes.schemas import CommandeResponse
from modules.panier import service

router = APIRouter(
    prefix="/panier",
    tags=["Panier"]
)

@router.post("/ajouter", response_model=PanierResponse, status_code=status.HTTP_200_OK)
def ajouter_livre(
    data: AjouterLivreSchema,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Ajouter un livre au panier (authentification requise)"""
    try:
        return service.ajouter_livre(db, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=PanierResponse)
def voir_panier(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Voir le panier (authentification requise)"""
    return service.voir_panier(db, current_user.id)

@router.get("/total", response_model=PanierTotalResponse)
def total_panier(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Obtenir le total du panier (authentification requise)"""
    return service.obtenir_total(db, current_user.id)

@router.delete("/retirer/{livre_id}", status_code=status.HTTP_200_OK)
def retirer_livre(
    livre_id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Retirer un livre du panier (authentification requise)"""
    return service.retirer_livre(db, current_user.id, livre_id)

@router.delete("/vider", status_code=status.HTTP_200_OK)
def vider_panier(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Vider le panier (authentification requise)"""
    return service.vider_panier(db, current_user.id)

@router.post("/commander", response_model=CommandeResponse, status_code=status.HTTP_201_CREATED)
def commander_panier(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Transformer le panier en commande (authentification requise)"""
    try:
        return service.commander_panier(db, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))