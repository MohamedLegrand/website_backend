from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class AccesLivreResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    livre_id: UUID
    commande_id: UUID
    accorde_le: datetime
    expire_le: Optional[datetime] = None

    class Config:
        from_attributes = True

class AccesLivreListResponse(BaseModel):
    total: int
    page: int
    taille: int
    acces: list[AccesLivreResponse]