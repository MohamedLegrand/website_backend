from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class AjouterLivreSchema(BaseModel):
    livre_id: UUID
    quantite: int = 1

class LignePanierResponse(BaseModel):
    id: UUID
    livre_id: UUID
    quantite: int
    ajoute_le: datetime

    class Config:
        from_attributes = True

class PanierResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    lignes: List[LignePanierResponse]
    total: float
    nombre_livres: int
    cree_le: datetime
    modifie_le: datetime

    class Config:
        from_attributes = True

class PanierTotalResponse(BaseModel):
    nombre_livres: int
    total: float