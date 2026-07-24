import hrpay
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.core.config import settings
from modules.paiements.models import Paiement
from modules.commandes.models import Commande
from modules.paiements.schemas import PaiementCreate
from modules.paiements.hrpay_client import get_client, devise_pour_pays
from modules.notifications.notifier import notifier
from modules.notifications.emails import envoyer_recu_paiement
from modules.utilisateurs.models import Utilisateur, RoleEnum

OPERATEURS_AUTORISES = {"ORANGE", "MTN"}


def _verifier_proprietaire_commande(db: Session, commande_id: UUID, utilisateur: Utilisateur) -> Commande:
    commande = db.execute(
        select(Commande).where(Commande.id == commande_id)
    ).scalar_one_or_none()

    if not commande:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commande non trouvée"
        )

    if commande.utilisateur_id != utilisateur.id and utilisateur.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette commande"
        )

    return commande


def obtenir_paiement_par_commande(db: Session, commande_id: UUID, utilisateur: Utilisateur) -> Paiement:
    paiement = db.execute(
        select(Paiement).where(Paiement.commande_id == commande_id)
    ).scalar_one_or_none()

    if not paiement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paiement non trouvé pour cette commande"
        )

    _verifier_proprietaire_commande(db, commande_id, utilisateur)

    # Synchronisation active en cas de polling : si le statut local est "en_attente",
    # on interroge l'API HR-Skills Pay pour obtenir le statut réel.
    if paiement.statut == "en_attente" and paiement.fournisseur_paiement_id:
        try:
            client = get_client()
            tx = client.transactions.get(reference=paiement.fournisseur_paiement_id)
            
            if tx.succeeded:
                data_webhook = {
                    "reference": tx.reference,
                    "operator": tx.operator,
                    "phone_number": tx.phone_number,
                    "amount": tx.amount,
                    "currency": tx.currency,
                    "fees": tx.fees,
                    "net_amount": tx.net_amount,
                    "status": tx.status_value,
                }
                _marquer_paiement_reussi(db, paiement, data_webhook)
            elif tx.failed:
                _marquer_paiement_echoue(db, paiement)
        except Exception:
            # On ignore discrètement les erreurs réseau/API temporaires pendant la lecture
            # pour ne pas bloquer l'affichage. Le webhook ou le polling suivant prendra le relais.
            pass

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


def initier_paiement(db: Session, commande_id: UUID, data: PaiementCreate, utilisateur: Utilisateur) -> Paiement:
    commande = _verifier_proprietaire_commande(db, commande_id, utilisateur)

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

    if data.operator.upper() not in OPERATEURS_AUTORISES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les paiements Orange Money et MTN Mobile Money sont acceptés"
        )

    devise_attendue = devise_pour_pays(data.country)
    if devise_attendue is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pays non supporté pour le paiement Mobile Money : {data.country}"
        )
    if devise_attendue != commande.devise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Devise incompatible : la commande est en {commande.devise}, "
                f"mais {data.country} utilise {devise_attendue}"
            )
        )

    paiement = Paiement(
        commande_id=commande_id,
        montant=float(commande.montant_total),
        devise=commande.devise,
        statut="en_attente",
        fournisseur="hrskillspay",
    )
    db.add(paiement)
    db.commit()
    db.refresh(paiement)

    try:
        reponse = get_client().cash_in.mobile_money(
            phone_number=data.phone_number,
            operator=data.operator.upper(),
            amount=float(commande.montant_total),
            currency=commande.devise,
            country=data.country.upper(),
            idempotency_key=f"cashin-{paiement.id}",
            metadata=data.metadonnees if isinstance(data.metadonnees, dict) else None,
        )
    except hrpay.ValidationError as e:
        paiement.statut = "echoue"
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except hrpay.RateLimitError:
        paiement.statut = "echoue"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives de paiement, réessayez dans quelques instants"
        )
    except (hrpay.NetworkError, hrpay.TimeoutError, hrpay.CircuitBreakerOpenError):
        paiement.statut = "echoue"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de paiement momentanément indisponible, réessayez plus tard"
        )
    except hrpay.HRPayError as e:
        paiement.statut = "echoue"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erreur du fournisseur de paiement : {e}"
        )

    paiement.fournisseur_paiement_id = reponse.reference
    paiement.metadonnees = {
        "operator": reponse.operator,
        "phone_number": reponse.phone_number,
        "fee": reponse.fee,
        "fee_percent": reponse.fee_percent,
        "net_amount": reponse.net_amount,
        "statut_fournisseur": reponse.status,
    }
    db.commit()
    db.refresh(paiement)
    return paiement


def traiter_webhook_paiement(db: Session, corps_brut: bytes, signature: str) -> dict:
    try:
        event = hrpay.construct_event(corps_brut, signature, settings.HRPAY_WEBHOOK_SECRET)
    except hrpay.WebhookSignatureError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    reference = event.data.get("reference")
    if not reference:
        return {"status": "ignored", "reason": "no reference in payload"}

    paiement = db.execute(
        select(Paiement).where(Paiement.fournisseur_paiement_id == reference)
    ).scalar_one_or_none()
    if not paiement:
        return {"status": "ignored", "reason": "paiement inconnu"}

    if event.type_value == "payment.succeeded":
        _marquer_paiement_reussi(db, paiement, event.data)
    elif event.type_value == "payment.failed":
        _marquer_paiement_echoue(db, paiement)
    elif event.type_value == "payment.hold":
        # Pas de statut dédié en base (contrainte CHECK limitée à
        # en_attente/reussi/echoue/rembourse) : on garde "en_attente"
        # et on trace le hold AML dans les métadonnées pour le support.
        paiement.metadonnees = {**(paiement.metadonnees or {}), "webhook_data": event.data, "hold": True}
        db.commit()
    elif event.type_value == "payment.refunded":
        _marquer_paiement_rembourse(db, paiement)

    return {"status": "ok"}


def _marquer_paiement_reussi(db: Session, paiement: Paiement, data: dict) -> None:
    if paiement.statut == "reussi":
        return  # déjà traité (webhook redélivré)

    paiement.statut = "reussi"
    paiement.paye_le = datetime.now(timezone.utc)
    paiement.metadonnees = {**(paiement.metadonnees or {}), "webhook_data": data}

    commande = db.execute(
        select(Commande).where(Commande.id == paiement.commande_id)
    ).scalar_one_or_none()
    if not commande:
        db.commit()
        return

    commande.statut = "payee"
    _accorder_acces_livres(db, commande)

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

    db.commit()
    db.refresh(commande)
    envoyer_recu_paiement(commande)


def _marquer_paiement_echoue(db: Session, paiement: Paiement) -> None:
    if paiement.statut == "reussi":
        return  # déjà payé, on ignore un échec tardif/redélivré
    paiement.statut = "echoue"
    db.commit()


def _marquer_paiement_rembourse(db: Session, paiement: Paiement) -> None:
    paiement.statut = "rembourse"
    commande = db.execute(
        select(Commande).where(Commande.id == paiement.commande_id)
    ).scalar_one_or_none()
    if commande:
        commande.statut = "remboursee"
    db.commit()


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
