from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
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

@router.post("/", response_model=UtilisateurResponse, status_code=status.HTTP_201_CREATED)
def creer_utilisateur(data: UtilisateurCreate, db: Session = Depends(get_db)):
    return service.creer_utilisateur(db, data)

@router.get("/me", response_model=UtilisateurResponse)
def mon_profil(utilisateur_id: UUID, db: Session = Depends(get_db)):
    return service.obtenir_utilisateur(db, utilisateur_id)

@router.put("/me", response_model=UtilisateurResponse)
def modifier_mon_profil(data: UtilisateurUpdate, utilisateur_id: UUID, db: Session = Depends(get_db)):
    return service.modifier_profil(db, utilisateur_id, data)

@router.patch("/me/avatar", response_model=UtilisateurResponse)
def changer_mon_avatar(data: UtilisateurUpdateAvatar, utilisateur_id: UUID, db: Session = Depends(get_db)):
    return service.changer_avatar(db, utilisateur_id, data.avatar_url)

@router.patch("/me/mot-de-passe", response_model=UtilisateurResponse)
def changer_mon_mot_de_passe(data: UtilisateurUpdateMotDePasse, utilisateur_id: UUID, db: Session = Depends(get_db)):
    return service.changer_mot_de_passe(db, utilisateur_id, data)

@router.delete("/me", status_code=status.HTTP_200_OK)
def supprimer_mon_compte(utilisateur_id: UUID, db: Session = Depends(get_db)):
    return service.supprimer_utilisateur(db, utilisateur_id)

# ─── Administration ───────────────────────────────────────────

@router.get("/", response_model=UtilisateurListResponse)
def liste_utilisateurs(page: int = 1, taille: int = 10, db: Session = Depends(get_db)):
    return service.obtenir_utilisateurs(db, page, taille)

@router.get("/{id}", response_model=UtilisateurResponse)
def obtenir_utilisateur(id: UUID, db: Session = Depends(get_db)):
    return service.obtenir_utilisateur(db, id)

@router.patch("/{id}/activer", response_model=UtilisateurResponse)
def activer_utilisateur(id: UUID, db: Session = Depends(get_db)):
    return service.activer_compte(db, id)

@router.patch("/{id}/desactiver", response_model=UtilisateurResponse)
def desactiver_utilisateur(id: UUID, db: Session = Depends(get_db)):
    return service.desactiver_compte(db, id)

@router.patch("/{id}/role", response_model=UtilisateurResponse)
def changer_role_utilisateur(id: UUID, data: UtilisateurUpdateRole, db: Session = Depends(get_db)):
    return service.changer_role(db, id, data)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def supprimer_utilisateur(id: UUID, db: Session = Depends(get_db)):
    return service.supprimer_utilisateur(db, id)