from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.database import get_db
from app.dependencies.auth import get_current_admin
from modules.utilisateurs.models import Utilisateur
from modules.collections.schemas import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionListResponse
)
from modules.collections import service

router = APIRouter(
    prefix="/collections",
    tags=["Collections"]
)

# Public
@router.get("/", response_model=CollectionListResponse)
def liste_collections(
    page: int = 1,
    taille: int = 10,
    db: Session = Depends(get_db)
):
    return service.obtenir_collections(db, page, taille)

@router.get("/{id}", response_model=CollectionResponse)
def obtenir_collection(
    id: UUID,
    db: Session = Depends(get_db)
):
    return service.obtenir_collection(db, id)

# Admin seulement
@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def creer_collection(
    data: CollectionCreate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.creer_collection(db, data)

@router.put("/{id}", response_model=CollectionResponse)
def modifier_collection(
    id: UUID,
    data: CollectionUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.modifier_collection(db, id, data)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def supprimer_collection(
    id: UUID,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(get_current_admin)
):
    return service.supprimer_collection(db, id)