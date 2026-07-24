from app.core.mail import envoyer_email_arriere_plan
from modules.commandes.models import Commande
from modules.commandes.facture import generer_facture_pdf, numero_facture


def _lignes_html(commande: Commande) -> str:
    lignes = []
    for ligne in commande.lignes:
        titre = ligne.livre.titre if ligne.livre else "Livre"
        sous_total = f"{ligne.quantite} × {ligne.prix_unitaire:,.0f} {commande.devise}".replace(",", " ")
        lignes.append(
            f"<tr><td style='padding:6px 0;border-bottom:1px solid #eee'>{titre}</td>"
            f"<td style='padding:6px 0;border-bottom:1px solid #eee;text-align:right;white-space:nowrap'>{sous_total}</td></tr>"
        )
    return "".join(lignes)


def envoyer_confirmation_commande(commande: Commande) -> None:
    utilisateur = commande.utilisateur
    if not utilisateur or not utilisateur.email:
        return

    total = f"{commande.montant_total:,.0f} {commande.devise}".replace(",", " ")
    corps = f"""
    <h2>Merci pour votre commande !</h2>
    <p>Bonjour {utilisateur.prenom or ''},</p>
    <p>Votre commande a bien été enregistrée. Voici le récapitulatif :</p>
    <table style="width:100%;border-collapse:collapse;margin:16px 0">
        {_lignes_html(commande)}
    </table>
    <p style="text-align:right;font-size:16px"><strong>Total : {total}</strong></p>
    <p>Vos livres seront disponibles dans votre bibliothèque dès la confirmation du paiement.</p>
    """
    envoyer_email_arriere_plan(
        utilisateur.email,
        "Confirmation de votre commande — Sagesse Africaine",
        corps,
    )


def envoyer_recu_paiement(commande: Commande) -> None:
    utilisateur = commande.utilisateur
    if not utilisateur or not utilisateur.email:
        return

    total = f"{commande.montant_total:,.0f} {commande.devise}".replace(",", " ")
    corps = f"""
    <h2>Paiement confirmé</h2>
    <p>Bonjour {utilisateur.prenom or ''},</p>
    <p>Votre paiement de <strong>{total}</strong> a bien été reçu.</p>
    <p>Vos livres sont maintenant disponibles dans votre bibliothèque.</p>
    <p>Vous trouverez votre facture en pièce jointe de cet email.</p>
    """

    pieces_jointes = None
    try:
        pdf = generer_facture_pdf(commande)
        pieces_jointes = [(f"{numero_facture(commande)}.pdf", pdf, "application/pdf")]
    except Exception:
        pass  # le reçu part quand même, sans la facture, plutôt que de ne rien envoyer

    envoyer_email_arriere_plan(
        utilisateur.email,
        "Reçu de paiement — Sagesse Africaine",
        corps,
        pieces_jointes,
    )
