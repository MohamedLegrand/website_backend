from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from fastapi import HTTPException, status
from modules.commandes.models import Commande, LigneCommande
from modules.livres.models import Livre
from modules.commandes.schemas import CommandeCreate, CommandeUpdateStatut

STATUTS_VALIDES = ["en_attente", "payee", "annulee", "remboursee"]

# Créer une commande
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
    db.commit()
    db.refresh(commande)
    return commande

# Obtenir toutes les commandes (admin)
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

# Obtenir les commandes d'un utilisateur
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

# Obtenir une commande par ID
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

# Annuler une commande
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
    db.commit()
    db.refresh(commande)
    return commande

# Changer le statut d'une commande (admin)
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
    commande.statut = data.statut
    db.commit()
    db.refresh(commande)
    return commande

# Supprimer une commande (admin)
def supprimer_commande(db: Session, commande_id: UUID) -> dict:
    commande = obtenir_commande(db, commande_id)
    db.delete(commande)
    db.commit()
    return {"message": "Commande supprimée avec succès"}