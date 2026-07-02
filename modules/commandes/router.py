from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.commandes.schemas import (
    CommandeCreate,
    CommandeUpdateStatut,
    CommandeResponse,
    CommandeListResponse
)
from modules.commandes import service
from modules.commandes.facture import generer_facture_pdf, numero_facture

router = APIRouter(
    prefix="/commandes",
    tags=["Commandes"]
)

# ─── Utilisateur connecté ─────────────────────────────────────

@router.post("/", response_model=CommandeResponse, status_code=status.HTTP_201_CREATED)
def creer_commande(
    data: CommandeCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.creer_commande(db, current_user.id, data)

@router.get("/mes-commandes", response_model=CommandeListResponse)
def mes_commandes(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.obtenir_mes_commandes(db, current_user.id, page, taille)

@router.get("/{id}", response_model=CommandeResponse)
def obtenir_commande(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.obtenir_commande_pour_utilisateur(db, id, current_user)

@router.patch("/{id}/annuler", response_model=CommandeResponse)
def annuler_commande(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    return service.annuler_commande(db, id, current_user.id)

@router.get("/{id}/facture")
def telecharger_facture(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Télécharge la facture PDF d'une commande payée (propriétaire ou admin uniquement)"""
    commande = service.obtenir_commande_pour_utilisateur(db, id, current_user)
    if commande.statut != "payee":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La facture n'est disponible que pour une commande payée"
        )
    pdf = generer_facture_pdf(commande)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{numero_facture(commande)}.pdf"'}
    )

# ─── Admin ────────────────────────────────────────────────────

@router.get("/", response_model=CommandeListResponse)
def liste_commandes(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.obtenir_commandes(db, page, taille)

@router.patch("/{id}/statut", response_model=CommandeResponse)
def changer_statut_commande(
    id: UUID,
    data: CommandeUpdateStatut,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.changer_statut_commande(db, id, data)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def supprimer_commande(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.supprimer_commande(db, id)