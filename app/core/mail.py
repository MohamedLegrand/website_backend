import smtplib
import threading
from email.message import EmailMessage
from email.utils import formataddr
from app.core.config import settings


def _envoyer_maintenant(
    destinataire: str,
    sujet: str,
    corps_html: str,
    pieces_jointes: list[tuple[str, bytes, str]] | None = None,
) -> None:
    message = EmailMessage()
    message["Subject"] = sujet
    message["From"] = formataddr((settings.MAIL_FROM_NAME, settings.MAIL_FROM))
    message["To"] = destinataire
    message.set_content("Ce message nécessite un client de messagerie compatible HTML.")
    message.add_alternative(corps_html, subtype="html")

    for nom_fichier, contenu, type_mime in (pieces_jointes or []):
        maintype, _, subtype = type_mime.partition("/")
        message.add_attachment(
            contenu, maintype=maintype, subtype=subtype or "octet-stream", filename=nom_fichier
        )

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        smtp.send_message(message)


def envoyer_email_arriere_plan(
    destinataire: str,
    sujet: str,
    corps_html: str,
    pieces_jointes: list[tuple[str, bytes, str]] | None = None,
) -> None:
    """
    Envoi non bloquant dans un thread daemon : ne doit jamais ralentir ou faire
    échouer un flux métier (commande, paiement...) à cause d'un souci SMTP.
    Les erreurs d'envoi sont donc volontairement avalées.
    """
    def _tache():
        try:
            _envoyer_maintenant(destinataire, sujet, corps_html, pieces_jointes)
        except Exception as erreur:
            # On n'interrompt jamais le flux métier pour un souci d'envoi d'email,
            # mais on ne veut pas non plus que l'échec soit totalement invisible.
            print(f"[mail] Échec d'envoi à {destinataire} ({sujet!r}) : {erreur}")

    threading.Thread(target=_tache, daemon=True).start()
