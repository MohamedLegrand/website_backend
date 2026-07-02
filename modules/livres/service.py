from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime
from modules.livres.models import Livre
from modules.collections.models import Collection
from modules.livres.schemas import LivreCreate, LivreUpdate
from modules.notifications.notifier import notifier
import re

def generer_slug(titre: str) -> str:
    slug = titre.lower()
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

def generer_slug_unique(db: Session, titre: str, exclude_id: UUID = None) -> str:
    base_slug = generer_slug(titre)
    slug = base_slug
    counter = 1
    while True:
        query = select(Livre).where(Livre.slug == slug)
        if exclude_id is not None:
            query = query.where(Livre.id != exclude_id)
        if not db.execute(query).scalar_one_or_none():
            return slug
        counter += 1
        slug = f"{base_slug}-{counter}"

def valider_slug_explicite(db: Session, slug: str, exclude_id: UUID = None) -> str:
    slug = slug.strip().lower()
    query = select(Livre).where(Livre.slug == slug)
    if exclude_id is not None:
        query = query.where(Livre.id != exclude_id)
    if db.execute(query).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un livre avec ce slug existe déjà"
        )
    return slug

# Créer un livre
def creer_livre(db: Session, data: LivreCreate, admin_id: UUID) -> Livre:
    if data.collection_id:
        collection = db.execute(
            select(Collection).where(Collection.id == data.collection_id)
        ).scalar_one_or_none()

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection non trouvée"
            )

    if data.isbn:
        existant = db.execute(
            select(Livre).where(Livre.isbn == data.isbn)
        ).scalar_one_or_none()

        if existant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un livre avec cet ISBN existe déjà"
            )

    if data.slug:
        slug = valider_slug_explicite(db, data.slug)
    else:
        slug = generer_slug_unique(db, data.titre)

    livre = Livre(
        titre=data.titre,
        slug=slug,
        auteur=data.auteur,
        description=data.description,
        couverture_url=data.couverture_url,
        quatrieme_couverture_url=data.quatrieme_couverture_url,
        sommaire_urls=data.sommaire_urls,
        langue=data.langue,
        isbn=data.isbn,
        prix=data.prix,
        est_gratuit=data.est_gratuit,
        collection_id=data.collection_id
    )
    db.add(livre)
    notifier(
        db, admin_id,
        titre="Livre ajouté",
        message=f"Le livre \"{data.titre}\" a été ajouté au catalogue avec succès.",
        type_notif="livre",
    )
    db.commit()
    db.refresh(livre)
    return livre

# Obtenir tous les livres
def obtenir_livres(db: Session, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(select(func.count(Livre.id))).scalar()
    livres = db.execute(
        select(Livre).offset(offset).limit(taille)
    ).scalars().all()

    return {
        "total": total,
        "page": page,
        "taille": taille,
        "livres": livres
    }

# Obtenir un livre par ID (UUID) ou par slug (ex: "ange-ou-demon")
def obtenir_livre(db: Session, id_ou_slug) -> Livre:
    livre = None

    if isinstance(id_ou_slug, UUID):
        livre = db.execute(
            select(Livre).where(Livre.id == id_ou_slug)
        ).scalar_one_or_none()
    else:
        try:
            livre_uuid = UUID(str(id_ou_slug))
        except ValueError:
            livre_uuid = None
        if livre_uuid is not None:
            livre = db.execute(
                select(Livre).where(Livre.id == livre_uuid)
            ).scalar_one_or_none()

    if livre is None:
        livre = db.execute(
            select(Livre).where(Livre.slug == str(id_ou_slug))
        ).scalar_one_or_none()

    if not livre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )
    return livre

# Obtenir les livres par collection
def obtenir_livres_par_collection(
    db: Session,
    collection_id: UUID,
    page: int = 1,
    taille: int = 10
) -> dict:
    offset = (page - 1) * taille
    total = db.execute(
        select(func.count(Livre.id)).where(Livre.collection_id == collection_id)
    ).scalar()
    livres = db.execute(
        select(Livre).where(
            Livre.collection_id == collection_id
        ).offset(offset).limit(taille)
    ).scalars().all()

    return {
        "total": total,
        "page": page,
        "taille": taille,
        "livres": livres
    }

# Modifier un livre
def modifier_livre(db: Session, livre_id: UUID, data: LivreUpdate, admin_id: UUID) -> Livre:
    livre = obtenir_livre(db, livre_id)

    if data.titre is not None:
        livre.titre = data.titre
        if data.slug is None:
            livre.slug = generer_slug_unique(db, data.titre, exclude_id=livre_id)
    if data.slug is not None:
        livre.slug = valider_slug_explicite(db, data.slug, exclude_id=livre_id)
    if data.auteur is not None:
        livre.auteur = data.auteur
    if data.description is not None:
        livre.description = data.description
    if data.couverture_url is not None:
        livre.couverture_url = data.couverture_url
    if data.quatrieme_couverture_url is not None:
        livre.quatrieme_couverture_url = data.quatrieme_couverture_url
    if data.sommaire_urls is not None:
        livre.sommaire_urls = data.sommaire_urls
    if data.langue is not None:
        livre.langue = data.langue
    if data.isbn is not None:
        if data.isbn != livre.isbn:
            existant = db.execute(
                select(Livre).where(Livre.isbn == data.isbn, Livre.id != livre_id)
            ).scalar_one_or_none()
            if existant:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Un livre avec cet ISBN existe déjà"
                )
        livre.isbn = data.isbn
    if data.prix is not None:
        livre.prix = data.prix
    if data.est_gratuit is not None:
        livre.est_gratuit = data.est_gratuit
    if data.collection_id is not None:
        livre.collection_id = data.collection_id

    notifier(
        db, admin_id,
        titre="Livre modifié",
        message=f"Le livre \"{livre.titre}\" a été mis à jour avec succès.",
        type_notif="livre",
    )
    db.commit()
    db.refresh(livre)
    return livre

# Publier un livre
def publier_livre(db: Session, livre_id: UUID) -> Livre:
    livre = obtenir_livre(db, livre_id)
    livre.est_publie = True
    livre.publie_le = datetime.utcnow()
    db.commit()
    db.refresh(livre)
    return livre

# Dépublier un livre
def depublier_livre(db: Session, livre_id: UUID) -> Livre:
    livre = obtenir_livre(db, livre_id)
    livre.est_publie = False
    db.commit()
    db.refresh(livre)
    return livre

# Supprimer un livre
def supprimer_livre(db: Session, livre_id: UUID, admin_id: UUID) -> dict:
    livre = obtenir_livre(db, livre_id)
    titre = livre.titre
    db.delete(livre)
    notifier(
        db, admin_id,
        titre="Livre supprimé",
        message=f"Le livre \"{titre}\" a été supprimé du catalogue.",
        type_notif="livre",
    )
    db.commit()
    return {"message": "Livre supprimé avec succès"}