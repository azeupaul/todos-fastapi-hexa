from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Schéma de base pour un utilisateur."""

    username: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True


class UserCreate(BaseModel):
    """Schéma pour la création d'un utilisateur."""

    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    """Schéma pour la connexion d'un utilisateur."""

    username: str
    password: str


class User(UserBase):
    """Schéma complet d'un utilisateur."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(User):
    """Schéma utilisateur avec mot de passe hashé (usage interne)."""

    hashed_password: str


class Token(BaseModel):
    """Schéma pour le token JWT."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schéma pour les données du token."""

    username: str | None = None
