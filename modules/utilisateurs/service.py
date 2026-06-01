from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.utilisateurs.models import Utilisateur, RoleEnum
from modules.utilisateurs.schemas import (
    UtilisateurCreate,
    UtilisateurUpdate,
    UtilisateurUpdateMotDePasse,
    UtilisateurUpdateRole
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hasher_mot_de_passe(mot_de_passe: str) -> str:
    return pwd_context.hash(mot_de_passe)

def verifier_mot_de_passe(mot_de_passe: str, hash: str) -> bool:
    return pwd_context.verify(mot_de_passe, hash)

# Créer un utilisateur
def creer_utilisateur(db: Session, data: UtilisateurCreate) -> Utilisateur:
    existant = db.execute(
        select(Utilisateur).where(Utilisateur.email == data.email)
    ).scalar_one_or_none()

    if existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )

    utilisateur = Utilisateur(
        email=data.email,
        mot_de_passe_hash=hasher_mot_de_passe(data.mot_de_passe),
        prenom=data.prenom,
        nom=data.nom
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# Récupérer un utilisateur par ID
def obtenir_utilisateur(db: Session, utilisateur_id: UUID) -> Utilisateur:
    utilisateur = db.execute(
        select(Utilisateur).where(Utilisateur.id == utilisateur_id)
    ).scalar_one_or_none()

    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return utilisateur

# Récupérer tous les utilisateurs avec pagination
def obtenir_utilisateurs(db: Session, page: int = 1, taille: int = 10):
    offset = (page - 1) * taille
    total = db.execute(select(func.count(Utilisateur.id))).scalar()
    utilisateurs = db.execute(
        select(Utilisateur).offset(offset).limit(taille)
    ).scalars().all()

    return {
        "total": total,
        "page": page,
        "taille": taille,
        "utilisateurs": utilisateurs
    }

# Modifier le profil
def modifier_profil(db: Session, utilisateur_id: UUID, data: UtilisateurUpdate) -> Utilisateur:
    utilisateur = obtenir_utilisateur(db, utilisateur_id)

    if data.prenom is not None:
        utilisateur.prenom = data.prenom
    if data.nom is not None:
        utilisateur.nom = data.nom

    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# Changer le mot de passe
def changer_mot_de_passe(db: Session, utilisateur_id: UUID, data: UtilisateurUpdateMotDePasse) -> Utilisateur:
    utilisateur = obtenir_utilisateur(db, utilisateur_id)

    if not verifier_mot_de_passe(data.ancien_mot_de_passe, utilisateur.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect"
        )

    utilisateur.mot_de_passe_hash = hasher_mot_de_passe(data.nouveau_mot_de_passe)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# Changer l'avatar
def changer_avatar(db: Session, utilisateur_id: UUID, avatar_url: str) -> Utilisateur:
    utilisateur = obtenir_utilisateur(db, utilisateur_id)
    utilisateur.avatar_url = avatar_url
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# Changer le rôle (admin)
def changer_role(db: Session, utilisateur_id: UUID, data: UtilisateurUpdateRole) -> Utilisateur:
    utilisateur = obtenir_utilisateur(db, utilisateur_id)
    utilisateur.role = data.role
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# Activer un compte
def activer_compte(db: Session, utilisateur_id: UUID) -> Utilisateur:
    utilisateur = obtenir_utilisateur(db, utilisateur_id)
    utilisateur.est_actif = True
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# Désactiver un compte
def desactiver_compte(db: Session, utilisateur_id: UUID) -> Utilisateur:
    utilisateur = obtenir_utilisateur(db, utilisateur_id)
    utilisateur.est_actif = False
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# Supprimer un compte
def supprimer_utilisateur(db: Session, utilisateur_id: UUID) -> dict:
    utilisateur = obtenir_utilisateur(db, utilisateur_id)
    db.delete(utilisateur)
    db.commit()
    return {"message": "Compte supprimé avec succès"}