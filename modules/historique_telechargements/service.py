from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from modules.historique_telechargements.models import HistoriqueTelechargement

def enregistrer_telechargement(
    db: Session,
    utilisateur_id: UUID,
    livre_id: UUID,
    fichier_livre_id: UUID,
    format: str,
    adresse_ip: str = None,
    appareil: str = None,
    systeme_exploitation: str = None
) -> HistoriqueTelechargement:
    historique = HistoriqueTelechargement(
        utilisateur_id=utilisateur_id,
        livre_id=livre_id,
        fichier_livre_id=fichier_livre_id,
        format=format,
        adresse_ip=adresse_ip,
        appareil=appareil,
        systeme_exploitation=systeme_exploitation
    )
    db.add(historique)
    db.commit()
    db.refresh(historique)
    return historique

def obtenir_mon_historique(db: Session, utilisateur_id: UUID, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(
        select(func.count(HistoriqueTelechargement.id)).where(
            HistoriqueTelechargement.utilisateur_id == utilisateur_id
        )
    ).scalar()
    historique = db.execute(
        select(HistoriqueTelechargement).where(
            HistoriqueTelechargement.utilisateur_id == utilisateur_id
        ).order_by(HistoriqueTelechargement.telecharge_le.desc()).offset(offset).limit(taille)
    ).scalars().all()

    return {"total": total, "page": page, "taille": taille, "historique": historique}

def obtenir_tout_historique(db: Session, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(select(func.count(HistoriqueTelechargement.id))).scalar()
    historique = db.execute(
        select(HistoriqueTelechargement).order_by(
            HistoriqueTelechargement.telecharge_le.desc()
        ).offset(offset).limit(taille)
    ).scalars().all()

    return {"total": total, "page": page, "taille": taille, "historique": historique}