from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status, UploadFile
from modules.fichiers_livres.models import FichierLivre
from modules.livres.models import Livre
from modules.livres import service as livres_service
from modules.acces_livres.models import AccesLivre
from modules.historique_telechargements import service as historique_service
from modules.utilisateurs.models import Utilisateur, RoleEnum
from app.core.config import settings
import os
import uuid
import aiofiles

FORMATS_AUTORISES = ["pdf", "epub"]

async def uploader_fichier(
    db: Session,
    livre_id: UUID,
    fichier: UploadFile
) -> FichierLivre:
    # Vérifier que le livre existe
    livre = db.execute(
        select(Livre).where(Livre.id == livre_id)
    ).scalar_one_or_none()

    if not livre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )

    # Vérifier le format
    extension = fichier.filename.split(".")[-1].lower()
    if extension not in FORMATS_AUTORISES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format non autorisé. Formats acceptés : {', '.join(FORMATS_AUTORISES)}"
        )

    # Vérifier si un fichier du même format existe déjà
    existant = db.execute(
        select(FichierLivre).where(
            FichierLivre.livre_id == livre_id,
            FichierLivre.format == extension
        )
    ).scalar_one_or_none()

    if existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un fichier {extension.upper()} existe déjà pour ce livre"
        )

    # Vérifier la taille du fichier
    contenu = await fichier.read()
    taille = len(contenu)
    taille_max = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if taille > taille_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux. Taille maximale : {settings.MAX_FILE_SIZE_MB} MB"
        )

    # Créer le dossier de stockage
    dossier = os.path.join(settings.UPLOAD_DIR, str(livre_id))
    os.makedirs(dossier, exist_ok=True)

    # Générer un nom de fichier unique
    nom_fichier = f"{uuid.uuid4()}.{extension}"
    chemin_fichier = os.path.join(dossier, nom_fichier)

    # Sauvegarder le fichier
    async with aiofiles.open(chemin_fichier, "wb") as f:
        await f.write(contenu)

    # Enregistrer en base de données
    fichier_livre = FichierLivre(
        livre_id=livre_id,
        format=extension,
        chemin_fichier=chemin_fichier,
        fournisseur_stockage="local",
        taille_octets=taille
    )
    db.add(fichier_livre)
    db.commit()
    db.refresh(fichier_livre)
    return fichier_livre

# Obtenir les fichiers d'un livre
def obtenir_fichiers_livre(db: Session, livre_id: UUID) -> dict:
    fichiers = db.execute(
        select(FichierLivre).where(FichierLivre.livre_id == livre_id)
    ).scalars().all()

    return {
        "total": len(fichiers),
        "fichiers": fichiers
    }

# Obtenir un fichier par ID
def obtenir_fichier(db: Session, fichier_id: UUID) -> FichierLivre:
    fichier = db.execute(
        select(FichierLivre).where(FichierLivre.id == fichier_id)
    ).scalar_one_or_none()

    if not fichier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier non trouvé"
        )
    return fichier

# Télécharger un fichier (livre acheté, gratuit, ou admin) — journalise le téléchargement
def telecharger_fichier(
    db: Session,
    id_ou_slug,
    fichier_id: UUID,
    utilisateur: Utilisateur,
    adresse_ip: str = None,
    appareil: str = None,
) -> tuple[Livre, FichierLivre]:
    livre = livres_service.obtenir_livre(db, id_ou_slug)

    fichier = obtenir_fichier(db, fichier_id)
    if fichier.livre_id != livre.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier non trouvé pour ce livre"
        )

    a_acces = livre.est_gratuit or utilisateur.role == RoleEnum.admin
    if not a_acces:
        acces = db.execute(
            select(AccesLivre).where(
                AccesLivre.utilisateur_id == utilisateur.id,
                AccesLivre.livre_id == livre.id
            )
        ).scalar_one_or_none()
        a_acces = acces is not None and (
            acces.expire_le is None or acces.expire_le > datetime.now(timezone.utc)
        )

    if not a_acces:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ce livre. Achetez-le pour pouvoir le télécharger."
        )

    historique_service.enregistrer_telechargement(
        db, utilisateur.id, livre.id, fichier.id, fichier.format,
        adresse_ip=adresse_ip, appareil=appareil
    )

    return livre, fichier

# Supprimer un fichier
def supprimer_fichier(db: Session, fichier_id: UUID) -> dict:
    fichier = obtenir_fichier(db, fichier_id)

    # Supprimer le fichier physique
    if os.path.exists(fichier.chemin_fichier):
        os.remove(fichier.chemin_fichier)

    db.delete(fichier)
    db.commit()
    return {"message": "Fichier supprimé avec succès"}