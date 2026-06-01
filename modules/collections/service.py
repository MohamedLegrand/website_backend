from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.collections.models import Collection
from modules.collections.schemas import CollectionCreate, CollectionUpdate
import re

def generer_slug(nom: str) -> str:
    slug = nom.lower()
    slug = re.sub(r'[àâä]', 'a', slug)
    slug = re.sub(r'[éèêë]', 'e', slug)
    slug = re.sub(r'[îï]', 'i', slug)
    slug = re.sub(r'[ôö]', 'o', slug)
    slug = re.sub(r'[ùûü]', 'u', slug)
    slug = re.sub(r'[ç]', 'c', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

# Créer une collection
def creer_collection(db: Session, data: CollectionCreate) -> Collection:
    existant = db.execute(
        select(Collection).where(Collection.nom == data.nom)
    ).scalar_one_or_none()

    if existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une collection avec ce nom existe déjà"
        )

    if data.collection_parent_id:
        parent = db.execute(
            select(Collection).where(Collection.id == data.collection_parent_id)
        ).scalar_one_or_none()

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection parente non trouvée"
            )

    slug = generer_slug(data.nom)

    collection = Collection(
        nom=data.nom,
        slug=slug,
        description=data.description,
        collection_parent_id=data.collection_parent_id
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection

# Obtenir toutes les collections
def obtenir_collections(db: Session, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(select(func.count(Collection.id))).scalar()
    collections = db.execute(
        select(Collection).offset(offset).limit(taille)
    ).scalars().all()

    return {
        "total": total,
        "page": page,
        "taille": taille,
        "collections": collections
    }

# Obtenir une collection par ID
def obtenir_collection(db: Session, collection_id: UUID) -> Collection:
    collection = db.execute(
        select(Collection).where(Collection.id == collection_id)
    ).scalar_one_or_none()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection non trouvée"
        )
    return collection

# Modifier une collection
def modifier_collection(db: Session, collection_id: UUID, data: CollectionUpdate) -> Collection:
    collection = obtenir_collection(db, collection_id)

    if data.nom is not None:
        existant = db.execute(
            select(Collection).where(
                Collection.nom == data.nom,
                Collection.id != collection_id
            )
        ).scalar_one_or_none()

        if existant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une collection avec ce nom existe déjà"
            )
        collection.nom = data.nom
        collection.slug = generer_slug(data.nom)

    if data.description is not None:
        collection.description = data.description

    if data.collection_parent_id is not None:
        collection.collection_parent_id = data.collection_parent_id

    db.commit()
    db.refresh(collection)
    return collection

# Supprimer une collection
def supprimer_collection(db: Session, collection_id: UUID) -> dict:
    collection = obtenir_collection(db, collection_id)
    db.delete(collection)
    db.commit()
    return {"message": "Collection supprimée avec succès"}