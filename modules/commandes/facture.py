import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.core.config import settings
from modules.commandes.models import Commande


def numero_facture(commande: Commande) -> str:
    return f"FACT-{str(commande.id)[:8].upper()}"


def generer_facture_pdf(commande: Commande) -> bytes:
    tampon = io.BytesIO()
    doc = SimpleDocTemplate(
        tampon, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    titre_style = ParagraphStyle("TitreFacture", parent=styles["Title"], fontSize=20, spaceAfter=2 * mm)
    normal = styles["Normal"]

    elements = []

    elements.append(Paragraph(settings.APP_NAME, titre_style))
    elements.append(Paragraph("FACTURE", ParagraphStyle("Sous-titre", parent=normal, fontSize=12, textColor=colors.grey)))
    elements.append(Spacer(1, 6 * mm))

    date_paiement = commande.paiement.paye_le if commande.paiement and commande.paiement.paye_le else commande.modifie_le
    infos = [
        ["N° de facture", numero_facture(commande)],
        ["Date", date_paiement.strftime("%d/%m/%Y") if date_paiement else "-"],
        ["Client", f"{commande.utilisateur.prenom or ''} {commande.utilisateur.nom or ''}".strip() or commande.utilisateur.email],
        ["Email", commande.utilisateur.email],
        ["Mode de paiement", (commande.paiement.fournisseur if commande.paiement and commande.paiement.fournisseur else "-")],
        ["Statut", "Payée" if commande.statut == "payee" else commande.statut],
    ]
    table_infos = Table(infos, colWidths=[45 * mm, 110 * mm])
    table_infos.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(table_infos)
    elements.append(Spacer(1, 8 * mm))

    lignes_table = [["Livre", "Prix unitaire", "Quantité", "Sous-total"]]
    for ligne in commande.lignes:
        sous_total = float(ligne.prix_unitaire) * ligne.quantite
        lignes_table.append([
            Paragraph(ligne.livre.titre, normal),
            f"{float(ligne.prix_unitaire):,.0f} {commande.devise}".replace(",", " "),
            str(ligne.quantite),
            f"{sous_total:,.0f} {commande.devise}".replace(",", " "),
        ])
    lignes_table.append(["", "", "Total", f"{float(commande.montant_total):,.0f} {commande.devise}".replace(",", " ")])

    table_lignes = Table(lignes_table, colWidths=[85 * mm, 30 * mm, 20 * mm, 30 * mm])
    table_lignes.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(table_lignes)
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph("Merci pour votre achat.", normal))

    doc.build(elements)
    return tampon.getvalue()
