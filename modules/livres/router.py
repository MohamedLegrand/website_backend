from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.livres.schemas import (
    LivreCreate,
    LivreUpdate,
    LivreResponse,
    LivreListResponse
)
from modules.livres import service

router = APIRouter(
    prefix="/livres",
    tags=["Livres"]
)

# ─── Public ───────────────────────────────────────────────────

@router.get("/", response_model=LivreListResponse)
def liste_livres(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db)
):
    return service.obtenir_livres(db, page, taille)

@router.get("/collection/{collection_id}", response_model=LivreListResponse)
def livres_par_collection(
    collection_id: UUID,
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db)
):
    return service.obtenir_livres_par_collection(db, collection_id, page, taille)

@router.get("/{id}", response_model=LivreResponse)
def obtenir_livre(
    id: UUID,
    db: Session = Depends(get_db)
):
    return service.obtenir_livre(db, id)

# ─── Admin ────────────────────────────────────────────────────

@router.post("/", response_model=LivreResponse, status_code=status.HTTP_201_CREATED)
def creer_livre(
    data: LivreCreate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.creer_livre(db, data)

@router.put("/{id}", response_model=LivreResponse)
def modifier_livre(
    id: UUID,
    data: LivreUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.modifier_livre(db, id, data)

@router.patch("/{id}/publier", response_model=LivreResponse)
def publier_livre(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.publier_livre(db, id)

@router.patch("/{id}/depublier", response_model=LivreResponse)
def depublier_livre(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.depublier_livre(db, id)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def supprimer_livre(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.supprimer_livre(db, id)