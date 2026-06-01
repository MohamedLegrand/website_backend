from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.database.database import engine
from modules.auth.router import router as auth_router
from modules.utilisateurs.router import router as utilisateurs_router
from modules.collections.router import router as collections_router
from modules.livres.router import router as livres_router
from modules.fichiers_livres.router import router as fichiers_livres_router
from modules.commandes.router import router as commandes_router
from modules.acces_livres.router import router as acces_livres_router
from modules.progression_lecture.router import router as progression_lecture_router
from modules.signets.router import router as signets_router
from modules.avis.router import router as avis_router
from modules.notifications.router import router as notifications_router
from modules.historique_telechargements.router import router as historique_router
import os

app = FastAPI(
    title=settings.APP_NAME,
    description="API backend pour l'application ebook",
    version=settings.APP_VERSION
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Inclusion des routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(utilisateurs_router, prefix="/api/v1")
app.include_router(collections_router, prefix="/api/v1")
app.include_router(livres_router, prefix="/api/v1")
app.include_router(fichiers_livres_router, prefix="/api/v1")
app.include_router(commandes_router, prefix="/api/v1")
app.include_router(acces_livres_router, prefix="/api/v1")
app.include_router(progression_lecture_router, prefix="/api/v1")
app.include_router(signets_router, prefix="/api/v1")
app.include_router(avis_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(historique_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
def root():
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
        "database": "connecté" if engine else "non connecté"
    }