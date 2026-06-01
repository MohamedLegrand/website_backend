from pydantic import BaseModel, EmailStr
from typing import Optional

# Inscription
class RegisterSchema(BaseModel):
    email: EmailStr
    mot_de_passe: str
    prenom: Optional[str] = None
    nom: Optional[str] = None

# Connexion
class LoginSchema(BaseModel):
    email: EmailStr
    mot_de_passe: str

# Token retourné après connexion
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Refresh token
class RefreshTokenSchema(BaseModel):
    refresh_token: str

# Oublier mot de passe
class OublierMotDePasseSchema(BaseModel):
    email: EmailStr

# Réinitialiser mot de passe
class ReinitialiserMotDePasseSchema(BaseModel):
    token: str
    nouveau_mot_de_passe: str