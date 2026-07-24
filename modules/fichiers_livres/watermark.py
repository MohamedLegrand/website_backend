from io import BytesIO
from datetime import datetime, timezone
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

def watermarker_pdf(chemin_source: str, identifiant_acheteur: str) -> bytes:
    """
    Incruste un filigrane discret (email de l'acheteur + horodatage) en pied de
    page de chaque page du PDF, pour dissuader et tracer la redistribution.
    """
    lecteur = PdfReader(chemin_source)
    ecrivain = PdfWriter()

    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    texte = f"Exemplaire personnel — {identifiant_acheteur} — {horodatage}"

    for page in lecteur.pages:
        largeur = float(page.mediabox.width)
        hauteur = float(page.mediabox.height)

        tampon = BytesIO()
        c = canvas.Canvas(tampon, pagesize=(largeur, hauteur))
        c.saveState()
        c.setFont("Helvetica", 7)
        c.setFillColorRGB(0.45, 0.45, 0.45)
        c.setFillAlpha(0.55)
        c.translate(largeur / 2, 10)
        c.drawCentredString(0, 0, texte)
        c.restoreState()
        c.save()
        tampon.seek(0)

        page_filigrane = PdfReader(tampon).pages[0]
        page.merge_page(page_filigrane)
        ecrivain.add_page(page)

    sortie = BytesIO()
    ecrivain.write(sortie)
    return sortie.getvalue()
