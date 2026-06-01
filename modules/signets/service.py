from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from fastapi import HTTPException, status
from modules.signets.models import Signet
from modules.signets.schemas import SignetCreate, SignetUpdate

def creer_signet(db: Session, utilisateur_id: UUID, data: SignetCreate) -> Signet:
    signet = Signet(
        utilisateur_id=utilisateur_id,
        livre_id=data.livre_id,
        format=data.format,
        numero_page=data.numero_page,
        position_epub_cfi=data.position_epub_cfi,
        note=data.note
    )
    db.add(signet)
    db.commit()
    db.refresh(signet)
    return signet

def obtenir_mes_signets(db: Session, utilisateur_id: UUID, livre_id: UUID = None) -> dict:
    query = select(Signet).where(Signet.utilisateur_id == utilisateur_id)
    if livre_id:
        query = query.where(Signet.livre_id == livre_id)
    signets = db.execute(query).scalars().all()
    return {"total": len(signets), "signets": signets}

def modifier_signet(db: Session, signet_id: UUID, utilisateur_id: UUID, data: SignetUpdate) -> Signet:
    signet = db.execute(
        select(Signet).where(Signet.id == signet_id, Signet.utilisateur_id == utilisateur_id)
    ).scalar_one_or_none()

    if not signet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signet non trouvé")

    if data.note is not None:
        signet.note = data.note

    db.commit()
    db.refresh(signet)
    return signet

def supprimer_signet(db: Session, signet_id: UUID, utilisateur_id: UUID) -> dict:
    signet = db.execute(
        select(Signet).where(Signet.id == signet_id, Signet.utilisateur_id == utilisateur_id)
    ).scalar_one_or_none()

    if not signet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signet non trouvé")

    db.delete(signet)
    db.commit()
    return {"message": "Signet supprimé avec succès"}