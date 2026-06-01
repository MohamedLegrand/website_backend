from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from modules.utilisateurs.models import Utilisateur, RoleEnum
from modules.auth.schemas import (
    RegisterSchema,
    LoginSchema,
    OublierMotDePasseSchema,
    ReinitialiserMotDePasseSchema
)
from app.core.config import settings
import bcrypt

# ─── Hash mot de passe ────────────────────────────────────────

def hasher_mot_de_passe(mot_de_passe: str) -> str:
    return bcrypt.hashpw(
        mot_de_passe.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verifier_mot_de_passe(mot_de_passe: str, hash: str) -> bool:
    return bcrypt.checkpw(
        mot_de_passe.encode("utf-8"),
        hash.encode("utf-8")
    )

# ─── JWT ──────────────────────────────────────────────────────

def creer_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def creer_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def creer_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    data = {"sub": email, "exp": expire, "type": "reset"}
    return jwt.encode(
        data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def verifier_token(token: str, type_token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != type_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )

# ─── Configuration Mail ───────────────────────────────────────

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def envoyer_email_reset(email: str, token: str):
    lien = f"http://localhost:3000/reinitialiser-mot-de-passe?token={token}"
    message = MessageSchema(
        subject="Réinitialisation de votre mot de passe",
        recipients=[email],
        body=f"""
        <h3>Réinitialisation de mot de passe</h3>
        <p>Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :</p>
        <a href="{lien}">{lien}</a>
        <p>Ce lien est valable pendant <strong>1 heure</strong>.</p>
        <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
        """,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# ─── Services ─────────────────────────────────────────────────

def register(db: Session, data: RegisterSchema) -> Utilisateur:
    existant = db.execute(
        select(Utilisateur).where(Utilisateur.email == data.email)
    ).scalar_one_or_none()

    if existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )

    utilisateur = Utilisateur(
        email=data.email,
        mot_de_passe_hash=hasher_mot_de_passe(data.mot_de_passe),
        prenom=data.prenom,
        nom=data.nom,
        role=RoleEnum.utilisateur
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

def login(db: Session, data: LoginSchema) -> dict:
    utilisateur = db.execute(
        select(Utilisateur).where(Utilisateur.email == data.email)
    ).scalar_one_or_none()

    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    if not verifier_mot_de_passe(data.mot_de_passe, utilisateur.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    if not utilisateur.est_actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé, contactez l'administrateur"
        )

    access_token = creer_access_token({"sub": str(utilisateur.id)})
    refresh_token = creer_refresh_token({"sub": str(utilisateur.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def refresh(refresh_token: str) -> dict:
    payload = verifier_token(refresh_token, "refresh")
    access_token = creer_access_token({"sub": payload["sub"]})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

async def oublier_mot_de_passe(db: Session, data: OublierMotDePasseSchema):
    utilisateur = db.execute(
        select(Utilisateur).where(Utilisateur.email == data.email)
    ).scalar_one_or_none()

    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte associé à cet email"
        )

    token = creer_reset_token(data.email)
    await envoyer_email_reset(data.email, token)
    return {"message": "Email de réinitialisation envoyé avec succès"}

async def reinitialiser_mot_de_passe(db: Session, data: ReinitialiserMotDePasseSchema):
    payload = verifier_token(data.token, "reset")
    email = payload.get("sub")

    utilisateur = db.execute(
        select(Utilisateur).where(Utilisateur.email == email)
    ).scalar_one_or_none()

    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    utilisateur.mot_de_passe_hash = hasher_mot_de_passe(data.nouveau_mot_de_passe)
    db.commit()
    return {"message": "Mot de passe réinitialisé avec succès"}