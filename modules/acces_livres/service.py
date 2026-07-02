from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.acces_livres.models import AccesLivre
from modules.livres import service as livres_service

def verifier_acces(db: Session, utilisateur_id: UUID, id_ou_slug) -> bool:
    livre = livres_service.obtenir_livre(db, id_ou_slug)
    acces = db.execute(
        select(AccesLivre).where(
            AccesLivre.utilisateur_id == utilisateur_id,
            AccesLivre.livre_id == livre.id
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

def _vers_reponse(acces: AccesLivre) -> dict:
    return {
        "id": acces.id,
        "utilisateur_id": acces.utilisateur_id,
        "livre_id": acces.livre_id,
        "commande_id": acces.commande_id,
        "accorde_le": acces.accorde_le,
        "expire_le": acces.expire_le,
        "livre": acces.livre,
        "fichiers_disponibles": acces.livre.fichiers if acces.livre else [],
    }

def obtenir_mes_acces(db: Session, utilisateur_id: UUID, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(
        select(func.count(AccesLivre.id)).where(AccesLivre.utilisateur_id == utilisateur_id)
    ).scalar()
    acces = db.execute(
        select(AccesLivre).where(
            AccesLivre.utilisateur_id == utilisateur_id
        ).order_by(AccesLivre.accorde_le.desc()).offset(offset).limit(taille)
    ).scalars().all()

    return {"total": total, "page": page, "taille": taille, "acces": [_vers_reponse(a) for a in acces]}

def obtenir_tous_acces(db: Session, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(select(func.count(AccesLivre.id))).scalar()
    acces = db.execute(select(AccesLivre).offset(offset).limit(taille)).scalars().all()
    return {"total": total, "page": page, "taille": taille, "acces": [_vers_reponse(a) for a in acces]}

def revoquer_acces(db: Session, acces_id: UUID) -> dict:
    acces = db.execute(
        select(AccesLivre).where(AccesLivre.id == acces_id)
    ).scalar_one_or_none()

    if not acces:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accès non trouvé")

    db.delete(acces)
    db.commit()
    return {"message": "Accès révoqué avec succès"}