from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.avis.models import Avis
from modules.avis.schemas import AvisCreate, AvisUpdate

def creer_avis(db: Session, utilisateur_id: UUID, data: AvisCreate) -> Avis:
    existant = db.execute(
        select(Avis).where(Avis.utilisateur_id == utilisateur_id, Avis.livre_id == data.livre_id)
    ).scalar_one_or_none()

    if existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà laissé un avis pour ce livre"
        )

    avis = Avis(
        utilisateur_id=utilisateur_id,
        livre_id=data.livre_id,
        note=data.note,
        commentaire=data.commentaire
    )
    db.add(avis)
    db.commit()
    db.refresh(avis)
    return avis

def obtenir_avis_livre(db: Session, livre_id: UUID, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(
        select(func.count(Avis.id)).where(Avis.livre_id == livre_id, Avis.est_approuve == True)
    ).scalar()
    avis = db.execute(
        select(Avis).where(
            Avis.livre_id == livre_id, Avis.est_approuve == True
        ).offset(offset).limit(taille)
    ).scalars().all()
    return {"total": total, "page": page, "taille": taille, "avis": avis}

def obtenir_tous_avis(db: Session, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(select(func.count(Avis.id))).scalar()
    avis = db.execute(select(Avis).offset(offset).limit(taille)).scalars().all()
    return {"total": total, "page": page, "taille": taille, "avis": avis}

def approuver_avis(db: Session, avis_id: UUID) -> Avis:
    avis = db.execute(select(Avis).where(Avis.id == avis_id)).scalar_one_or_none()
    if not avis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avis non trouvé")
    avis.est_approuve = True
    db.commit()
    db.refresh(avis)
    return avis

def supprimer_avis(db: Session, avis_id: UUID) -> dict:
    avis = db.execute(select(Avis).where(Avis.id == avis_id)).scalar_one_or_none()
    if not avis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avis non trouvé")
    db.delete(avis)
    db.commit()
    return {"message": "Avis supprimé avec succès"}