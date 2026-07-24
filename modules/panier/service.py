from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from modules.panier.models import Panier, LignePanier
from modules.livres.models import Livre
from modules.livres import service as livres_service
from modules.panier.schemas import AjouterLivreSchema, PanierResponse, LignePanierResponse
from fastapi import HTTPException, status
from modules.acces_livres.service import verifier_acces


def obtenir_ou_creer_panier(db: Session, utilisateur_id: UUID) -> Panier:
    """Récupère ou crée un panier pour l'utilisateur"""
    panier = db.query(Panier).filter(Panier.utilisateur_id == utilisateur_id).first()
    if not panier:
        panier = Panier(utilisateur_id=utilisateur_id)
        db.add(panier)
        db.commit()
        db.refresh(panier)
    return panier


def ajouter_livre(db: Session, utilisateur_id: UUID, data: AjouterLivreSchema):
    """Ajoute un livre au panier"""
    panier = obtenir_ou_creer_panier(db, utilisateur_id)

    # Vérifier si le livre existe (livre_id accepte un UUID ou un slug)
    livre = livres_service.obtenir_livre(db, data.livre_id)

    # Vérifier si le livre est gratuit
    if livre.est_gratuit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les livres gratuits ne peuvent pas être ajoutés au panier. Vous pouvez y accéder directement."
        )

    # Vérifier si l'utilisateur possède déjà le livre
    if verifier_acces(db, utilisateur_id, livre.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous possédez déjà ce livre"
        )

    # Vérifier si le livre est déjà dans le panier
    ligne = db.query(LignePanier).filter(
        LignePanier.panier_id == panier.id,
        LignePanier.livre_id == livre.id
    ).first()

    if ligne:
        ligne.quantite = 1
    else:
        ligne = LignePanier(
            panier_id=panier.id,
            livre_id=livre.id,
            quantite=1
        )
        db.add(ligne)

    db.commit()
    return convertir_en_reponse(db, panier.id)


def voir_panier(db: Session, utilisateur_id: UUID):
    """Voir le panier de l'utilisateur"""
    panier = db.query(Panier).filter(Panier.utilisateur_id == utilisateur_id).first()
    if not panier:
        return PanierResponse(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            utilisateur_id=utilisateur_id,
            lignes=[],
            total=0,
            nombre_livres=0,
            cree_le=None,
            modifie_le=None
        )
    return convertir_en_reponse(db, panier.id)


def obtenir_total(db: Session, utilisateur_id: UUID):
    """Obtenir le total du panier"""
    panier = db.query(Panier).filter(Panier.utilisateur_id == utilisateur_id).first()
    if not panier:
        return {"nombre_livres": 0, "total": 0}

    lignes = db.query(LignePanier).filter(LignePanier.panier_id == panier.id).all()
    total = 0
    nombre = 0

    for ligne in lignes:
        if ligne.livre:
            total += ligne.quantite * (ligne.livre.prix or 0)
            nombre += ligne.quantite

    return {"nombre_livres": nombre, "total": total}


def retirer_livre(db: Session, utilisateur_id: UUID, livre_id: UUID):
    """Retirer un livre du panier"""
    panier = db.query(Panier).filter(Panier.utilisateur_id == utilisateur_id).first()
    if not panier:
        return {"message": "Panier vide"}

    db.query(LignePanier).filter(
        LignePanier.panier_id == panier.id,
        LignePanier.livre_id == livre_id
    ).delete()
    db.commit()
    return {"message": "Livre retiré du panier"}


def vider_panier(db: Session, utilisateur_id: UUID):
    """Vider le panier"""
    panier = db.query(Panier).filter(Panier.utilisateur_id == utilisateur_id).first()
    if panier:
        db.query(LignePanier).filter(LignePanier.panier_id == panier.id).delete()
        db.commit()
    return {"message": "Panier vidé"}


def commander_panier(db: Session, utilisateur_id: UUID):
    """Transformer le panier en commande"""
    from modules.commandes import service as commandes_service

    panier = db.query(Panier).filter(Panier.utilisateur_id == utilisateur_id).first()
    if not panier or not panier.lignes:
        raise ValueError("Panier vide")

    # Créer la commande
    commande = commandes_service.creer_commande_depuis_panier(db, utilisateur_id, panier)

    # Vider le panier
    db.query(LignePanier).filter(LignePanier.panier_id == panier.id).delete()
    db.commit()

    return commande


def convertir_en_reponse(db: Session, panier_id: UUID):
    """Convertit le panier en réponse"""
    lignes = db.query(LignePanier).filter(LignePanier.panier_id == panier_id).all()
    panier = db.query(Panier).filter(Panier.id == panier_id).first()

    lignes_response = []
    total = 0
    nombre = 0

    for ligne in lignes:
        if ligne.livre:
            lignes_response.append(LignePanierResponse(
                id=ligne.id,
                livre_id=ligne.livre_id,
                quantite=ligne.quantite,
                ajoute_le=ligne.ajoute_le
            ))
            total += ligne.quantite * (ligne.livre.prix or 0)
            nombre += ligne.quantite

    return PanierResponse(
        id=panier.id,
        utilisateur_id=panier.utilisateur_id,
        lignes=lignes_response,
        total=total,
        nombre_livres=nombre,
        cree_le=panier.cree_le,
        modifie_le=panier.modifie_le
    )