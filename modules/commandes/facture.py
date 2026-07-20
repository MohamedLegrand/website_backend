import io
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from app.core.config import settings
from modules.commandes.models import Commande

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def numero_facture(commande: Commande) -> str:
    return f"FACT-{str(commande.id)[:8].upper()}"


def _chemin_logo() -> Path | None:
    chemin = Path(settings.FACTURE_LOGO_PATH)
    if not chemin.is_absolute():
        chemin = BASE_DIR / chemin
    return chemin if chemin.is_file() else None


def _formater_montant(montant: float, devise: str) -> str:
    return f"{montant:,.2f} {devise}".replace(",", " ")


def generer_facture_pdf(commande: Commande) -> bytes:
    tampon = io.BytesIO()
    doc = SimpleDocTemplate(
        tampon, pagesize=A4,
        topMargin=15 * mm, bottomMargin=15 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    petit_gris = ParagraphStyle("PetitGris", parent=normal, fontSize=8, textColor=colors.grey)
    entreprise_nom_style = ParagraphStyle("EntrepriseNom", parent=styles["Title"], fontSize=18, leading=22, alignment=TA_RIGHT)
    entreprise_slogan_style = ParagraphStyle("EntrepriseSlogan", parent=normal, fontSize=8, textColor=colors.HexColor("#b8860b"), alignment=TA_RIGHT, fontName="Helvetica-Oblique")
    facture_titre_style = ParagraphStyle("FactureTitre", parent=styles["Title"], fontSize=16, textColor=colors.HexColor("#1f2937"))

    elements = []

    # ─── En-tête : logo + identité entreprise ─────────────────
    logo_chemin = _chemin_logo()
    entreprise_lignes = [Paragraph(settings.FACTURE_ENTREPRISE_NOM, entreprise_nom_style)]
    if settings.FACTURE_ENTREPRISE_SLOGAN:
        entreprise_lignes.append(Paragraph(settings.FACTURE_ENTREPRISE_SLOGAN, entreprise_slogan_style))

    if logo_chemin:
        logo = Image(str(logo_chemin), width=30 * mm, height=30 * mm, kind="proportional")
        entete = Table([[logo, entreprise_lignes]], colWidths=[35 * mm, 105 * mm])
        entete.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ]))
        elements.append(entete)
    else:
        elements.append(Paragraph(settings.FACTURE_ENTREPRISE_NOM, ParagraphStyle("EntrepriseNomSeul", parent=styles["Title"], fontSize=18)))

    elements.append(Spacer(1, 6 * mm))
    elements.append(Paragraph("FACTURE", facture_titre_style))
    elements.append(Spacer(1, 6 * mm))

    # ─── Informations facture / client ─────────────────────────
    date_paiement = commande.paiement.paye_le if commande.paiement and commande.paiement.paye_le else commande.modifie_le
    client_nom = f"{commande.utilisateur.prenom or ''} {commande.utilisateur.nom or ''}".strip() or commande.utilisateur.email

    infos_facture = [
        ["N° de facture", numero_facture(commande)],
        ["N° de commande", str(commande.id)],
        ["Date", date_paiement.strftime("%d/%m/%Y") if date_paiement else "-"],
        ["Statut", "Payée" if commande.statut == "payee" else commande.statut],
        ["Mode de paiement", (commande.paiement.fournisseur if commande.paiement and commande.paiement.fournisseur else "-")],
    ]
    infos_client = [
        ["Facturé à", ""],
        ["Nom", client_nom],
        ["Email", commande.utilisateur.email],
    ]

    table_facture = Table(infos_facture, colWidths=[35 * mm, 45 * mm])
    table_facture.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    table_client = Table(infos_client, colWidths=[25 * mm, 55 * mm])
    table_client.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (1, 0), 0.5, colors.grey),
    ]))

    table_entete_infos = Table([[table_facture, table_client]], colWidths=[85 * mm, 65 * mm])
    table_entete_infos.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(table_entete_infos)
    elements.append(Spacer(1, 10 * mm))

    # ─── Détail des livres ──────────────────────────────────────
    lignes_table = [["Livre", "Auteur", "ISBN", "Prix unit.", "Qté", "Sous-total"]]
    for ligne in commande.lignes:
        sous_total = float(ligne.prix_unitaire) * ligne.quantite
        lignes_table.append([
            Paragraph(ligne.livre.titre, normal),
            Paragraph(ligne.livre.auteur or "-", normal),
            ligne.livre.isbn or "-",
            _formater_montant(float(ligne.prix_unitaire), commande.devise),
            str(ligne.quantite),
            _formater_montant(sous_total, commande.devise),
        ])
    lignes_table.append(["", "", "", "", "Total", _formater_montant(float(commande.montant_total), commande.devise)])

    table_lignes = Table(lignes_table, colWidths=[52 * mm, 35 * mm, 23 * mm, 22 * mm, 13 * mm, 30 * mm])
    table_lignes.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (4, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(table_lignes)
    elements.append(Spacer(1, 12 * mm))
    elements.append(Paragraph("Merci pour votre confiance et votre achat.", normal))

    # ─── Pied de page entreprise ────────────────────────────────
    pied_lignes = [l for l in [
        settings.FACTURE_ENTREPRISE_ADRESSE,
        " · ".join(filter(None, [settings.FACTURE_ENTREPRISE_TELEPHONE, settings.FACTURE_ENTREPRISE_EMAIL, settings.FACTURE_ENTREPRISE_SITE_WEB])),
    ] if l]
    if pied_lignes:
        elements.append(Spacer(1, 10 * mm))
        for ligne in pied_lignes:
            elements.append(Paragraph(ligne, petit_gris))

    doc.build(elements)
    return tampon.getvalue()
