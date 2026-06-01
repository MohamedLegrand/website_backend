from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class SignetCreate(BaseModel):
    livre_id: UUID
    format: str
    numero_page: Optional[int] = None
    position_epub_cfi: Optional[str] = None
    note: Optional[str] = None

class SignetUpdate(BaseModel):
    note: Optional[str] = None

class SignetResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    livre_id: UUID
    format: str
    numero_page: Optional[int] = None
    position_epub_cfi: Optional[str] = None
    note: Optional[str] = None
    cree_le: datetime

    class Config:
        from_attributes = True

class SignetListResponse(BaseModel):
    total: int
    signets: list[SignetResponse]