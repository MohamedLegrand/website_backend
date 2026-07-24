from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application
    APP_NAME: str = "Website Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Upload fichiers (livres PDF/EPUB) — accès protégé, jamais servi en statique
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50

    # Upload fichiers publics (images de couverture) — dossier distinct de UPLOAD_DIR,
    # servi en statique sans authentification. Ne jamais y stocker de fichiers de livres.
    PUBLIC_UPLOAD_DIR: str = "uploads_public"
    MAX_IMAGE_SIZE_MB: int = 5

    # Téléchargements de livres achetés
    LIMITE_TELECHARGEMENTS_PAR_LIVRE: int = 5

    # Facturation (en-tête / pied de page du PDF de facture)
    FACTURE_ENTREPRISE_NOM: str = "Sagesse Africaine"
    FACTURE_ENTREPRISE_SLOGAN: str = "Un peuple qui maîtrise ses savoirs maîtrise aussi son destin"
    FACTURE_ENTREPRISE_ADRESSE: str = ""
    FACTURE_ENTREPRISE_TELEPHONE: str = ""
    FACTURE_ENTREPRISE_EMAIL: str = ""
    FACTURE_ENTREPRISE_SITE_WEB: str = ""
    FACTURE_LOGO_PATH: str = "app/static/images/logo.png"

    # Mail
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Website Backend"

    # HR-Skills Pay (paiements Mobile Money)
    HRPAY_PUBLIC_KEY: str = ""
    HRPAY_SECRET_KEY: str = ""
    HRPAY_WEBHOOK_SECRET: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()