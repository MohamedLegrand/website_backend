from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class PaiementCreate(BaseModel):
    operator: str
    phone_number: str
    country: str = "CM"
    metadonnees: Optional[Any] = None


class PaiementResponse(BaseModel):
    id: UUID
    commande_id: UUID
    fournisseur: Optional[str] = None
    fournisseur_paiement_id: Optional[str] = None
    statut: str
    montant: float
    devise: str
    metadonnees: Optional[Any] = None
    paye_le: Optional[datetime] = None
    cree_le: datetime

    class Config:
        from_attributes = True


class PaiementListResponse(BaseModel):
    total: int
    page: int
    taille: int
    paiements: list[PaiementResponse]
