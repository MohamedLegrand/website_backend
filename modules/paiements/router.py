from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.paiements.schemas import (
    PaiementCreate,
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


@router.post("/webhook/hrskillspay", status_code=status.HTTP_200_OK)
async def webhook_hrskillspay(
    request: Request,
    db: Session = Depends(get_db),
):
    """Appelé par HR-Skills Pay (serveur à serveur) — pas d'authentification JWT.
    La signature HMAC du corps brut fait foi (voir service.traiter_webhook_paiement)."""
    corps_brut = await request.body()
    signature = request.headers.get("X-Hub-Signature", "")
    return service.traiter_webhook_paiement(db, corps_brut, signature)


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
