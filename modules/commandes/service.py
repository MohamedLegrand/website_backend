from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.commandes.models import Commande, LigneCommande
from modules.livres.models import Livre
from modules.commandes.schemas import CommandeCreate, CommandeUpdateStatut
from modules.notifications.notifier import notifier

STATUTS_VALIDES = ["en_attente", "payee", "annulee", "remboursee"]


def creer_commande(db: Session, utilisateur_id: UUID, data: CommandeCreate) -> Commande:
    if not data.lignes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La commande doit contenir au moins un livre"
        )

    montant_total = 0.0
    lignes = []

    for ligne in data.lignes:
        livre = db.execute(
            select(Livre).where(Livre.id == ligne.livre_id)
        ).scalar_one_or_none()

        if not livre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livre {ligne.livre_id} non trouvé"
            )

        if not livre.est_publie:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le livre '{livre.titre}' n'est pas disponible"
            )

        prix = 0.0 if livre.est_gratuit else float(livre.prix)
        montant_total += prix * ligne.quantite

        lignes.append(LigneCommande(
            livre_id=ligne.livre_id,
            prix_unitaire=prix,
            quantite=ligne.quantite
        ))

    commande = Commande(
        utilisateur_id=utilisateur_id,
        statut="en_attente",
        montant_total=montant_total,
        devise=data.devise,
        lignes=lignes
    )
    db.add(commande)
    notifier(
        db, utilisateur_id,
        titre="Commande passée avec succès",
        message=f"Votre commande a été enregistrée. Total : {montant_total:.2f} {data.devise}.",
        type_notif="commande",
        lien=f"/commandes/{commande.id}",
    )
    db.commit()
    db.refresh(commande)
    return commande


def creer_commande_depuis_panier(db: Session, utilisateur_id: UUID, panier) -> Commande:
    if not panier.lignes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le panier est vide"
        )

    montant_total = 0.0
    lignes = []

    for ligne in panier.lignes:
        livre = ligne.livre
        if not livre:
            continue
        if not livre.est_publie:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le livre '{livre.titre}' n'est pas disponible"
            )
        prix = 0.0 if livre.est_gratuit else float(livre.prix or 0)
        montant_total += prix * ligne.quantite
        lignes.append(LigneCommande(
            livre_id=ligne.livre_id,
            prix_unitaire=prix,
            quantite=ligne.quantite
        ))

    commande = Commande(
        utilisateur_id=utilisateur_id,
        statut="en_attente",
        montant_total=montant_total,
        devise="EUR",
        lignes=lignes
    )
    db.add(commande)
    notifier(
        db, utilisateur_id,
        titre="Commande passée avec succès",
        message=f"Votre commande a été enregistrée. Total : {montant_total:.2f} EUR.",
        type_notif="commande",
        lien=f"/commandes/{commande.id}",
    )
    db.commit()
    db.refresh(commande)
    return commande


def obtenir_commandes(db: Session, page: int = 1, taille: int = 10) -> dict:
    offset = (page - 1) * taille
    total = db.execute(select(func.count(Commande.id))).scalar()
    commandes = db.execute(
        select(Commande).offset(offset).limit(taille)
    ).scalars().all()

    return {
        "total": total,
        "page": page,
        "taille": taille,
        "commandes": commandes
    }


def obtenir_mes_commandes(
    db: Session,
    utilisateur_id: UUID,
    page: int = 1,
    taille: int = 10
) -> dict:
    offset = (page - 1) * taille
    total = db.execute(
        select(func.count(Commande.id)).where(
            Commande.utilisateur_id == utilisateur_id
        )
    ).scalar()
    commandes = db.execute(
        select(Commande).where(
            Commande.utilisateur_id == utilisateur_id
        ).offset(offset).limit(taille)
    ).scalars().all()

    return {
        "total": total,
        "page": page,
        "taille": taille,
        "commandes": commandes
    }


def obtenir_commande(db: Session, commande_id: UUID) -> Commande:
    commande = db.execute(
        select(Commande).where(Commande.id == commande_id)
    ).scalar_one_or_none()

    if not commande:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande non trouvée"
        )
    return commande


def annuler_commande(db: Session, commande_id: UUID, utilisateur_id: UUID) -> Commande:
    commande = obtenir_commande(db, commande_id)

    if commande.utilisateur_id != utilisateur_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette commande"
        )

    if commande.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seules les commandes en attente peuvent être annulées"
        )

    commande.statut = "annulee"
    notifier(
        db, utilisateur_id,
        titre="Commande annulée",
        message="Votre commande a été annulée.",
        type_notif="commande",
        lien=f"/commandes/{commande_id}",
    )
    db.commit()
    db.refresh(commande)
    return commande


def changer_statut_commande(
    db: Session,
    commande_id: UUID,
    data: CommandeUpdateStatut
) -> Commande:
    if data.statut not in STATUTS_VALIDES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statut invalide. Statuts valides : {', '.join(STATUTS_VALIDES)}"
        )

    commande = obtenir_commande(db, commande_id)
    ancien_statut = commande.statut
    commande.statut = data.statut

    if data.statut == "payee" and ancien_statut != "payee":
        _accorder_acces_livres(db, commande, commande_id)
        notifier(
            db, commande.utilisateur_id,
            titre="Paiement confirmé !",
            message=(
                "Votre paiement a été confirmé. "
                "Vos livres sont maintenant disponibles dans votre bibliothèque."
            ),
            type_notif="paiement",
            lien="/bibliotheque",
        )
    elif data.statut == "annulee" and ancien_statut != "annulee":
        notifier(
            db, commande.utilisateur_id,
            titre="Commande annulée",
            message="Votre commande a été annulée par notre équipe.",
            type_notif="commande",
            lien=f"/commandes/{commande_id}",
        )
    elif data.statut == "remboursee" and ancien_statut != "remboursee":
        notifier(
            db, commande.utilisateur_id,
            titre="Remboursement effectué",
            message=(
                "Votre commande a été remboursée. "
                "Le montant sera crédité sous 3 à 5 jours ouvrés."
            ),
            type_notif="paiement",
            lien=f"/commandes/{commande_id}",
        )

    db.commit()
    db.refresh(commande)
    return commande


def supprimer_commande(db: Session, commande_id: UUID) -> dict:
    commande = obtenir_commande(db, commande_id)
    db.delete(commande)
    db.commit()
    return {"message": "Commande supprimée avec succès"}


def _accorder_acces_livres(db: Session, commande: Commande, commande_id: UUID) -> None:
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
                commande_id=commande_id
            ))
