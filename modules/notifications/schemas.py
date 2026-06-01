from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class NotificationCreate(BaseModel):
    utilisateur_id: UUID
    titre: str
    message: str
    type: str
    lien: Optional[str] = None

class NotificationResponse(BaseModel):
    id: UUID
    utilisateur_id: UUID
    titre: str
    message: str
    type: str
    est_lu: bool
    lien: Optional[str] = None
    cree_le: datetime

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    total: int
    non_lues: int
    notifications: list[NotificationResponse]