from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

# Ligne de commande
class LigneCommandeCreate(BaseModel):
    livre_id: UUID
    quantite: int = 1

class LigneCommandeResponse(BaseModel):
    id: UUID
    livre_id: UUID
    prix_unitaire: float
    quantite: int

    class Config:
        from_attributes = True

# Commande
class CommandeCreate(BaseModel):
    lignes: list[LigneCommandeCreate]
    devise: str = "EUR"

class CommandeUpdateStatut(BaseModel):
    statut: str

class CommandeResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    statut: str
    montant_total: float
    devise: str
    lignes: list[LigneCommandeResponse]
    cree_le: datetime
    modifie_le: datetime

    class Config:
        from_attributes = True

class CommandeListResponse(BaseModel):
    total: int
    page: int
    taille: int
    commandes: list[CommandeResponse]