from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_user, get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.utilisateurs.schemas import (
    UtilisateurCreate,
    UtilisateurUpdate,
    UtilisateurUpdateMotDePasse,
    UtilisateurUpdateAvatar,
    UtilisateurUpdateRole,
    UtilisateurResponse,
    UtilisateurListResponse
)
from modules.utilisateurs import service

router = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"]
)

# ─── Profil personnel ─────────────────────────────────────────

@router.get("/me", response_model=UtilisateurResponse)
def mon_profil(
    current_user: Utilisateur = Depends(get_current_user)
):
    return current_user

@router.put("/me", response_model=UtilisateurResponse)
def modifier_mon_profil(
    data: UtilisateurUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.modifier_profil(db, current_user.id, data)

@router.patch("/me/avatar", response_model=UtilisateurResponse)
def changer_mon_avatar(
    data: UtilisateurUpdateAvatar,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.changer_avatar(db, current_user.id, data.avatar_url)

@router.patch("/me/mot-de-passe", response_model=UtilisateurResponse)
def changer_mon_mot_de_passe(
    data: UtilisateurUpdateMotDePasse,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.changer_mot_de_passe(db, current_user.id, data)

@router.delete("/me", status_code=status.HTTP_200_OK)
def supprimer_mon_compte(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.supprimer_utilisateur(db, current_user.id)

# ─── Administration ───────────────────────────────────────────

@router.post("/", response_model=UtilisateurResponse, status_code=status.HTTP_201_CREATED)
def creer_utilisateur(
    data: UtilisateurCreate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.creer_utilisateur(db, data)

@router.get("/", response_model=UtilisateurListResponse)
def liste_utilisateurs(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.obtenir_utilisateurs(db, page, taille)

@router.get("/{id}", response_model=UtilisateurResponse)
def obtenir_utilisateur(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.obtenir_utilisateur(db, id)

@router.patch("/{id}/activer", response_model=UtilisateurResponse)
def activer_utilisateur(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.activer_compte(db, id)

@router.patch("/{id}/desactiver", response_model=UtilisateurResponse)
def desactiver_utilisateur(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.desactiver_compte(db, id)

@router.patch("/{id}/role", response_model=UtilisateurResponse)
def changer_role_utilisateur(
    id: UUID,
    data: UtilisateurUpdateRole,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.changer_role(db, id, data)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def supprimer_utilisateur(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.supprimer_utilisateur(db, id)