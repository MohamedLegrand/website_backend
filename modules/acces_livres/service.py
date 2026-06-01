from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.acces_livres.models import AccesLivre

def verifier_acces(db: Session, utilisateur_id: UUID, livre_id: UUID) -> bool:
    acces = db.execute(
        select(AccesLivre).where(
            AccesLivre.utilisateur_id == utilisateur_id,
            AccesLivre.livre_id == livre_id
        )
    ).scalar_one_or_none()
    return acces is not None

def creer_acces(db: Session, utilisateur_id: UUID, livre_id: UUID, commande_id: UUID) -> AccesLivre:
    existant = db.execute(
        select(AccesLivre).where(
            AccesLivre.utilisateur_id == utilisateur_id,
            AccesLivre.livre_id == livre_id
        )
    ).scalar_one_or_none()

    if existant:
        return existant

    acces = AccesLivre(
        utilisateur_id=utilisateur_id,
        livre_id=livre_id,
        commande_id=commande_id
    )
    db.add(acces)
    db.commit()
    db.refresh(acces)
    return acces

def obtenir_mes_acces(db: Session, utilisateur_id: UUID, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(
        select(func.count(AccesLivre.id)).where(AccesLivre.utilisateur_id == utilisateur_id)
    ).scalar()
    acces = db.execute(
        select(AccesLivre).where(
            AccesLivre.utilisateur_id == utilisateur_id
        ).offset(offset).limit(taille)
    ).scalars().all()

    return {"total": total, "page": page, "taille": taille, "acces": acces}

def obtenir_tous_acces(db: Session, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(select(func.count(AccesLivre.id))).scalar()
    acces = db.execute(select(AccesLivre).offset(offset).limit(taille)).scalars().all()
    return {"total": total, "page": page, "taille": taille, "acces": acces}

def revoquer_acces(db: Session, acces_id: UUID) -> dict:
    acces = db.execute(
        select(AccesLivre).where(AccesLivre.id == acces_id)
    ).scalar_one_or_none()

    if not acces:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accès non trouvé")

    db.delete(acces)
    db.commit()
    return {"message": "Accès révoqué avec succès"}