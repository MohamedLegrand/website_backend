from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from modules.utilisateurs.models import RoleEnum

# Schéma de base
class UtilisateurBase(BaseModel):
    email: EmailStr
    prenom: Optional[str] = None
    nom: Optional[str] = None

# Schéma pour la création
class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

# Schéma pour la modification du profil
class UtilisateurUpdate(BaseModel):
    prenom: Optional[str] = None
    nom: Optional[str] = None

# Schéma pour changer le mot de passe
class UtilisateurUpdateMotDePasse(BaseModel):
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str

# Schéma pour changer l'avatar
class UtilisateurUpdateAvatar(BaseModel):
    avatar_url: str

# Schéma pour changer le rôle (admin)
class UtilisateurUpdateRole(BaseModel):
    role: RoleEnum

# Schéma de réponse (ce qu'on renvoie au client)
class UtilisateurResponse(UtilisateurBase):
    id: UUID
    role: RoleEnum
    avatar_url: Optional[str] = None
    est_actif: bool
    cree_le: datetime
    modifie_le: datetime

    class Config:
        from_attributes = True

# Schéma de réponse liste
class UtilisateurListResponse(BaseModel):
    total: int
    page: int
    taille: int
    utilisateurs: list[UtilisateurResponse]