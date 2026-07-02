from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class LivreResumeSchema(BaseModel):
    id: UUID
    slug: str
    titre: str
    auteur: str
    couverture_url: Optional[str] = None

    class Config:
        from_attributes = True

class FichierResumeSchema(BaseModel):
    id: UUID
    format: str

    class Config:
        from_attributes = True

class AccesLivreResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    livre_id: UUID
    commande_id: UUID
    accorde_le: datetime
    expire_le: Optional[datetime] = None
    livre: Optional[LivreResumeSchema] = None
    fichiers_disponibles: list[FichierResumeSchema] = []

    class Config:
        from_attributes = True

class AccesLivreListResponse(BaseModel):
    total: int
    page: int
    taille: int
    acces: list[AccesLivreResponse]