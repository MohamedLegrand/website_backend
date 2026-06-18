from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.paiements.schemas import (
    PaiementCreate,
    PaiementConfirmer,
    PaiementResponse,
    PaiementListResponse,
)
from modules.paiements import service

router = APIRouter(prefix="/paiements", tags=["Paiements"])


@router.post(
    "/{commande_id}/initier",
    response_model=PaiementResponse,
    status_code=status.HTTP_201_CREATED,
)
def initier_paiement(
    commande_id: UUID,
    data: PaiementCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return service.initier_paiement(db, commande_id, data)


@router.post("/{paiement_id}/confirmer", response_model=PaiementResponse)
def confirmer_paiement(
    paiement_id: UUID,
    data: PaiementConfirmer,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return service.confirmer_paiement(db, paiement_id, current_user.id, data)


@router.get("/commande/{commande_id}", response_model=PaiementResponse)
def paiement_par_commande(
    commande_id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    return service.obtenir_paiement_par_commande(db, commande_id)


@router.get("/", response_model=PaiementListResponse)
def tous_les_paiements(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin),
):
    return service.obtenir_tous_paiements(db, page, taille)
