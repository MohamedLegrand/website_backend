from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

class ProgressionCreate(BaseModel):
    livre_id: UUID
    format: str
    page_actuelle: Optional[int] = None
    total_pages: Optional[int] = None
    pourcentage: float = 0.0
    position_epub_cfi: Optional[Any] = None

class ProgressionUpdate(BaseModel):
    page_actuelle: Optional[int] = None
    total_pages: Optional[int] = None
    pourcentage: Optional[float] = None
    position_epub_cfi: Optional[Any] = None

class ProgressionResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    livre_id: UUID
    format: str
    page_actuelle: Optional[int] = None
    total_pages: Optional[int] = None
    pourcentage: float
    position_epub_cfi: Optional[Any] = None
    derniere_lecture_le: datetime

    class Config:
        from_attributes = True

class ProgressionListResponse(BaseModel):
    total: int
    progressions: list[ProgressionResponse]