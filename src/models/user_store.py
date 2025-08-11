"""Stockage en mémoire pour les utilisateurs."""
from datetime import datetime
from typing import Dict

from src.auth.security import get_password_hash, verify_password
from src.schemas.user import User, UserCreate, UserInDB


class UserStore:
    """Stockage simple en mémoire pour les utilisateurs."""

    def __init__(self):
        self._users: Dict[int, UserInDB] = {}
        self._users_by_username: Dict[str, UserInDB] = {}
        self._users_by_email: Dict[str, UserInDB] = {}
        self._next_id = 1

    def create_user(self, user_data: UserCreate) -> User:
        """Créer un nouvel utilisateur."""
        # Vérifier que l'utilisateur n'existe pas déjà
        if user_data.username in self._users_by_username:
            raise ValueError("Un utilisateur avec ce nom d'utilisateur existe déjà")

        if user_data.email in self._users_by_email:
            raise ValueError("Un utilisateur avec cet email existe déjà")

        # Créer l'utilisateur
        now = datetime.now()
        hashed_password = get_password_hash(user_data.password)

        user_in_db = UserInDB(
            id=self._next_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=True,
            created_at=now,
            hashed_password=hashed_password,
        )

        # Stocker l'utilisateur
        self._users[self._next_id] = user_in_db
        self._users_by_username[user_data.username] = user_in_db
        self._users_by_email[user_data.email] = user_in_db
        self._next_id += 1

        # Retourner l'utilisateur sans le mot de passe
        return User(
            id=user_in_db.id,
            username=user_in_db.username,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
        )

    def get_user_by_username(self, username: str) -> UserInDB | None:
        """Récupérer un utilisateur par son nom d'utilisateur."""
        return self._users_by_username.get(username)

    def get_user_by_email(self, email: str) -> UserInDB | None:
        """Récupérer un utilisateur par son email."""
        return self._users_by_email.get(email)

    def get_user_by_id(self, user_id: int) -> User | None:
        """Récupérer un utilisateur par son ID."""
        user_in_db = self._users.get(user_id)
        if not user_in_db:
            return None

        return User(
            id=user_in_db.id,
            username=user_in_db.username,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
        )

    def authenticate_user(self, username: str, password: str) -> UserInDB | None:
        """Authentifier un utilisateur."""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user


# Instance globale pour cette phase
user_store = UserStore()
