from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.progression_lecture.models import ProgressionLecture
from modules.progression_lecture.schemas import ProgressionCreate, ProgressionUpdate

def creer_ou_mettre_a_jour(db: Session, utilisateur_id: UUID, data: ProgressionCreate) -> ProgressionLecture:
    progression = db.execute(
        select(ProgressionLecture).where(
            ProgressionLecture.utilisateur_id == utilisateur_id,
            ProgressionLecture.livre_id == data.livre_id
        )
    ).scalar_one_or_none()

    if progression:
        if data.page_actuelle is not None:
            progression.page_actuelle = data.page_actuelle
        if data.total_pages is not None:
            progression.total_pages = data.total_pages
        if data.pourcentage is not None:
            progression.pourcentage = data.pourcentage
        if data.position_epub_cfi is not None:
            progression.position_epub_cfi = data.position_epub_cfi
    else:
        progression = ProgressionLecture(
            utilisateur_id=utilisateur_id,
            livre_id=data.livre_id,
            format=data.format,
            page_actuelle=data.page_actuelle,
            total_pages=data.total_pages,
            pourcentage=data.pourcentage,
            position_epub_cfi=data.position_epub_cfi
        )
        db.add(progression)

    db.commit()
    db.refresh(progression)
    return progression

def obtenir_mes_progressions(db: Session, utilisateur_id: UUID) -> dict:
    progressions = db.execute(
        select(ProgressionLecture).where(
            ProgressionLecture.utilisateur_id == utilisateur_id
        )
    ).scalars().all()
    return {"total": len(progressions), "progressions": progressions}

def obtenir_progression_livre(db: Session, utilisateur_id: UUID, livre_id: UUID) -> ProgressionLecture:
    progression = db.execute(
        select(ProgressionLecture).where(
            ProgressionLecture.utilisateur_id == utilisateur_id,
            ProgressionLecture.livre_id == livre_id
        )
    ).scalar_one_or_none()

    if not progression:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progression non trouvée")
    return progression

def supprimer_progression(db: Session, utilisateur_id: UUID, livre_id: UUID) -> dict:
    progression = obtenir_progression_livre(db, utilisateur_id, livre_id)
    db.delete(progression)
    db.commit()
    return {"message": "Progression supprimée avec succès"}