from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from modules.auth.schemas import (
    RegisterSchema,
    LoginSchema,
    TokenSchema,
    RefreshTokenSchema,
    OublierMotDePasseSchema,
    ReinitialiserMotDePasseSchema
)
from modules.auth import service

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    return service.register(db, data)

@router.post("/login", response_model=TokenSchema)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    return service.login(db, data)

@router.post("/refresh", response_model=TokenSchema)
def refresh(data: RefreshTokenSchema):
    return service.refresh(data.refresh_token)

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    return {"message": "Déconnexion réussie"}

@router.post("/oublier-mot-de-passe", status_code=status.HTTP_200_OK)
async def oublier_mot_de_passe(data: OublierMotDePasseSchema, db: Session = Depends(get_db)):
    return await service.oublier_mot_de_passe(db, data)

@router.post("/reinitialiser-mot-de-passe", status_code=status.HTTP_200_OK)
async def reinitialiser_mot_de_passe(data: ReinitialiserMotDePasseSchema, db: Session = Depends(get_db)):
    return await service.reinitialiser_mot_de_passe(db, data)