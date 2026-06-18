from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status
from modules.paiements.models import Paiement
from modules.commandes.models import Commande
from modules.paiements.schemas import PaiementCreate, PaiementConfirmer
from modules.notifications.notifier import notifier


def obtenir_paiement_par_commande(db: Session, commande_id: UUID) -> Paiement:
    paiement = db.execute(
        select(Paiement).where(Paiement.commande_id == commande_id)
    ).scalar_one_or_none()

    if not paiement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paiement non trouvé pour cette commande"
        )
    return paiement


def obtenir_tous_paiements(db: Session, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(select(func.count(Paiement.id))).scalar()
    paiements = db.execute(
        select(Paiement).offset(offset).limit(taille)
    ).scalars().all()

    return {
        "total": total,
        "page": page,
        "taille": taille,
        "paiements": paiements
    }


def initier_paiement(db: Session, commande_id: UUID, data: PaiementCreate) -> Paiement:
    commande = db.execute(
        select(Commande).where(Commande.id == commande_id)
    ).scalar_one_or_none()

    if not commande:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande non trouvée"
        )

    if commande.statut not in ("en_attente",):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette commande ne peut pas être payée (statut invalide)"
        )

    existant = db.execute(
        select(Paiement).where(
            Paiement.commande_id == commande_id,
            Paiement.statut == "en_attente"
        )
    ).scalar_one_or_none()
    if existant:
        return existant

    paiement = Paiement(
        commande_id=commande_id,
        montant=float(commande.montant_total),
        devise=commande.devise,
        statut="en_attente",
        fournisseur=data.fournisseur,
        fournisseur_paiement_id=data.fournisseur_paiement_id,
        metadonnees=data.metadonnees,
    )
    db.add(paiement)
    db.commit()
    db.refresh(paiement)
    return paiement


def confirmer_paiement(
    db: Session,
    paiement_id: UUID,
    utilisateur_id: UUID,
    data: PaiementConfirmer,
) -> Paiement:
    paiement = db.execute(
        select(Paiement).where(Paiement.id == paiement_id)
    ).scalar_one_or_none()

    if not paiement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paiement non trouvé"
        )

    if paiement.statut == "complete":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce paiement est déjà confirmé"
        )

    commande = db.execute(
        select(Commande).where(Commande.id == paiement.commande_id)
    ).scalar_one_or_none()

    if not commande or commande.utilisateur_id != utilisateur_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )

    # Mettre à jour le paiement
    paiement.statut = "complete"
    paiement.paye_le = datetime.now(timezone.utc)
    if data.fournisseur_paiement_id:
        paiement.fournisseur_paiement_id = data.fournisseur_paiement_id
    if data.metadonnees:
        paiement.metadonnees = data.metadonnees

    # Mettre à jour la commande
    commande.statut = "payee"

    # Accorder l'accès aux livres
    _accorder_acces_livres(db, commande)

    # Notification
    notifier(
        db, utilisateur_id,
        titre="Paiement confirmé !",
        message=(
            "Votre paiement a été confirmé. "
            "Vos livres sont maintenant disponibles dans votre bibliothèque."
        ),
        type_notif="paiement",
        lien="/bibliotheque",
    )

    db.commit()
    db.refresh(paiement)
    return paiement


def _accorder_acces_livres(db: Session, commande: Commande) -> None:
    from modules.acces_livres.models import AccesLivre
    for ligne in commande.lignes:
        existant = db.execute(
            select(AccesLivre).where(
                AccesLivre.utilisateur_id == commande.utilisateur_id,
                AccesLivre.livre_id == ligne.livre_id
            )
        ).scalar_one_or_none()
        if not existant:
            db.add(AccesLivre(
                utilisateur_id=commande.utilisateur_id,
                livre_id=ligne.livre_id,
                commande_id=commande.id
            ))
