from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_admin, get_current_user
from modules.utilisateurs.models import Utilisateur
from modules.fichiers_livres.schemas import (
    FichierLivreResponse,
    FichierLivreListResponse
)
from modules.fichiers_livres import service

router = APIRouter(
    prefix="/fichiers-livres",
    tags=["Fichiers Livres"]
)

# ─── Admin ────────────────────────────────────────────────────

@router.post(
    "/{livre_id}/upload",
    response_model=FichierLivreResponse,
    status_code=status.HTTP_201_CREATED
)
async def uploader_fichier(
    livre_id: UUID,
    fichier: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return await service.uploader_fichier(db, livre_id, fichier)

@router.delete("/{fichier_id}", status_code=status.HTTP_200_OK)
def supprimer_fichier(
    fichier_id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.supprimer_fichier(db, fichier_id)

# ─── Public ───────────────────────────────────────────────────

@router.get("/{livre_id}", response_model=FichierLivreListResponse)
def liste_fichiers_livre(
    livre_id: UUID,
    db: Session = Depends(get_db)
):
    return service.obtenir_fichiers_livre(db, livre_id)

# ─── Utilisateur connecté ─────────────────────────────────────

@router.get(
    "/{livre_id}/telecharger/{fichier_id}",
    response_class=FileResponse
)
def telecharger_fichier(
    livre_id: UUID,
    fichier_id: UUID,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    fichier = service.obtenir_fichier(db, fichier_id)
    return FileResponse(
        path=fichier.chemin_fichier,
        filename=f"livre.{fichier.format}",
        media_type="application/octet-stream"
    )