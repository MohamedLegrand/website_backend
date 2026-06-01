from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class FichierLivreResponse(BaseModel):
    id: UUID
    livre_id: UUID
    format: str
    chemin_fichier: str
    fournisseur_stockage: Optional[str] = None
    taille_octets: Optional[int] = None
    televerse_le: datetime

    class Config:
        from_attributes = True

class FichierLivreListResponse(BaseModel):
    total: int
    fichiers: list[FichierLivreResponse]