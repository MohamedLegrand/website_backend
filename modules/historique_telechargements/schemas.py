from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class HistoriqueResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    livre_id: UUID
    fichier_livre_id: UUID
    format: str
    adresse_ip: Optional[str] = None
    appareil: Optional[str] = None
    systeme_exploitation: Optional[str] = None
    telecharge_le: datetime

    class Config:
        from_attributes = True

class HistoriqueListResponse(BaseModel):
    total: int
    page: int
    taille: int
    historique: list[HistoriqueResponse]