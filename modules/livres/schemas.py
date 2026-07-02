from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

# Schéma de base
class LivreBase(BaseModel):
    titre: str
    auteur: str
    description: Optional[str] = None
    couverture_url: Optional[str] = None
    quatrieme_couverture_url: Optional[str] = None
    sommaire_urls: Optional[list[str]] = None
    langue: Optional[str] = None
    isbn: Optional[str] = None
    prix: float
    est_gratuit: bool = False
    collection_id: Optional[UUID] = None

# Schéma de création
class LivreCreate(LivreBase):
    # Optionnel : impose un slug explicite au lieu de le générer depuis le titre
    # (nécessaire pour faire correspondre les ids statiques du frontend)
    slug: Optional[str] = None

# Schéma de modification
class LivreUpdate(BaseModel):
    titre: Optional[str] = None
    slug: Optional[str] = None
    auteur: Optional[str] = None
    description: Optional[str] = None
    couverture_url: Optional[str] = None
    quatrieme_couverture_url: Optional[str] = None
    sommaire_urls: Optional[list[str]] = None
    langue: Optional[str] = None
    isbn: Optional[str] = None
    prix: Optional[float] = None
    est_gratuit: Optional[bool] = None
    collection_id: Optional[UUID] = None

# Schéma de réponse
class LivreResponse(LivreBase):
    id: UUID
    slug: str
    est_publie: bool
    publie_le: Optional[datetime] = None
    cree_le: datetime
    modifie_le: datetime

    class Config:
        from_attributes = True

# Schéma de réponse liste
class LivreListResponse(BaseModel):
    total: int
    page: int
    taille: int
    livres: list[LivreResponse]