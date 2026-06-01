from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# Schéma de base
class CollectionBase(BaseModel):
    nom: str
    description: Optional[str] = None
    collection_parent_id: Optional[UUID] = None

# Schéma de création
class CollectionCreate(CollectionBase):
    pass

# Schéma de modification
class CollectionUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    collection_parent_id: Optional[UUID] = None

# Schéma de réponse
class CollectionResponse(CollectionBase):
    id: UUID
    slug: str
    collection_parent_id: Optional[UUID] = None

    class Config:
        from_attributes = True

# Schéma de réponse liste
class CollectionListResponse(BaseModel):
    total: int
    page: int
    taille: int
    collections: list[CollectionResponse]