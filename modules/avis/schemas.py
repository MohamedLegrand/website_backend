from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class AvisCreate(BaseModel):
    livre_id: str  # UUID ou slug (ex: "ange-ou-demon")
    note: int = Field(..., ge=1, le=5)
    commentaire: Optional[str] = None

class AvisUpdate(BaseModel):
    note: Optional[int] = Field(None, ge=1, le=5)
    commentaire: Optional[str] = None

class AvisResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    livre_id: UUID
    note: int
    commentaire: Optional[str] = None
    est_approuve: bool
    cree_le: datetime

    class Config:
        from_attributes = True

class AvisListResponse(BaseModel):
    total: int
    page: int
    taille: int
    avis: list[AvisResponse]