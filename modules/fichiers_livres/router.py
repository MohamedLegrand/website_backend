from fastapi import APIRouter, Depends, Request, UploadFile, File, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Literal
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
    livre_id: str,
    db: Session = Depends(get_db)
):
    """livre_id accepte soit l'UUID en base, soit le slug"""
    from modules.livres import service as livres_service
    livre = livres_service.obtenir_livre(db, livre_id)
    return service.obtenir_fichiers_livre(db, livre.id)

# ─── Utilisateur connecté ─────────────────────────────────────

MEDIA_TYPES = {
    "pdf": "application/pdf",
    "epub": "application/epub+zip",
}

@router.get("/{livre_id}/telecharger/{fichier_id}")
def telecharger_fichier(
    livre_id: str,
    fichier_id: UUID,
    request: Request,
    mode: Literal["lecture", "telechargement"] = "telechargement",
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    livre_id accepte soit l'UUID en base, soit le slug.
    Nécessite un accès valide (livre gratuit, acheté, ou compte admin).

    mode="lecture" (lecteur en ligne) : illimité, fichier non filigrané.
    mode="telechargement" (par défaut) : soumis au quota de téléchargements
    et filigrané (PDF) avec l'email de l'acheteur.
    """
    livre, fichier, contenu_filigrane = service.telecharger_fichier(
        db, livre_id, fichier_id, current_user, mode=mode,
        adresse_ip=request.client.host if request.client else None,
        appareil=request.headers.get("user-agent"),
    )

    nom_fichier = f"{livre.slug}.{fichier.format}"
    media_type = MEDIA_TYPES.get(fichier.format, "application/octet-stream")

    if contenu_filigrane is not None:
        disposition = "attachment" if mode == "telechargement" else "inline"
        return Response(
            content=contenu_filigrane,
            media_type=media_type,
            headers={"Content-Disposition": f'{disposition}; filename="{nom_fichier}"'}
        )

    return FileResponse(
        path=fichier.chemin_fichier,
        filename=nom_fichier,
        media_type=media_type
    )