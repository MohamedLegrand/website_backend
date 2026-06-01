from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.database.database import engine
from modules.utilisateurs.router import router as utilisateurs_router
import os

app = FastAPI(
    title=settings.APP_NAME,
    description="API backend pour l'application ebook",
    version=settings.APP_VERSION
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Inclusion des routers
app.include_router(utilisateurs_router, prefix="/api/v1")

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