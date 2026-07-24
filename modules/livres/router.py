from fastapi import APIRouter, Depends, Request, UploadFile, File, status
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
    recherche: str | None = None,
    db: Session = Depends(get_db)
):
    return service.obtenir_livres(db, page, taille, recherche)

@router.get("/collection/{collection_id}", response_model=LivreListResponse)
def livres_par_collection(
    collection_id: UUID,
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db)
):
    return service.obtenir_livres_par_collection(db, collection_id, page, taille)

# ─── Admin ────────────────────────────────────────────────────
# Déclarée avant /{id} pour que "admin" ne soit pas interprété comme un identifiant de livre.

@router.get("/admin", response_model=LivreListResponse)
def liste_livres_admin(
    page: int = 1,
    taille: int = 10,
    recherche: str | None = None,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    """Catalogue complet (publiés + brouillons), réservé à l'administration."""
    return service.obtenir_livres_admin(db, page, taille, recherche)

# ─── Public ───────────────────────────────────────────────────

@router.get("/{id}", response_model=LivreResponse)
def obtenir_livre(
    id: str,
    db: Session = Depends(get_db)
):
    """id accepte soit l'UUID en base, soit le slug (ex: "ange-ou-demon")"""
    return service.obtenir_livre(db, id)

# ─── Admin ────────────────────────────────────────────────────

@router.post("/", response_model=LivreResponse, status_code=status.HTTP_201_CREATED)
def creer_livre(
    data: LivreCreate,
    db: Session = Depends(get_db),
    current_admin: Utilisateur = Depends(get_current_admin)
):
    return service.creer_livre(db, data, current_admin.id)

@router.put("/{id}", response_model=LivreResponse)
def modifier_livre(
    id: str,
    data: LivreUpdate,
    db: Session = Depends(get_db),
    current_admin: Utilisateur = Depends(get_current_admin)
):
    livre = service.obtenir_livre(db, id)
    return service.modifier_livre(db, livre.id, data, current_admin.id)

@router.patch("/{id}/publier", response_model=LivreResponse)
def publier_livre(
    id: str,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    livre = service.obtenir_livre(db, id)
    return service.publier_livre(db, livre.id)

@router.patch("/{id}/depublier", response_model=LivreResponse)
def depublier_livre(
    id: str,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    livre = service.obtenir_livre(db, id)
    return service.depublier_livre(db, livre.id)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def supprimer_livre(
    id: str,
    db: Session = Depends(get_db),
    current_admin: Utilisateur = Depends(get_current_admin)
):
    livre = service.obtenir_livre(db, id)
    return service.supprimer_livre(db, livre.id, current_admin.id)

@router.post("/{id}/couverture", response_model=LivreResponse)
async def televerser_couverture(
    id: str,
    request: Request,
    fichier: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    livre = service.obtenir_livre(db, id)
    return await service.televerser_couverture(db, livre.id, fichier, str(request.base_url))