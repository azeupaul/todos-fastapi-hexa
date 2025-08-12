"""Tests pour les utilitaires de sécurité."""
from datetime import timedelta

from src.auth.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)


def test_password_hashing():
    """Test du hashage et de la vérification des mots de passe."""
    password = "mysecretpassword"

    # Hasher le mot de passe
    hashed = get_password_hash(password)

    # Le hash ne doit pas être identique au mot de passe original
    assert hashed != password
    assert len(hashed) > 0

    # La vérification doit fonctionner
    assert verify_password(password, hashed) is True

    # Un mauvais mot de passe doit échouer
    assert verify_password("wrongpassword", hashed) is False


def test_password_hash_different_each_time():
    """Test que le hash est différent à chaque fois (salt)."""
    password = "samepassword"

    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Les hash doivent être différents (grâce au salt)
    assert hash1 != hash2

    # Mais la vérification doit fonctionner pour les deux
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_create_access_token():
    """Test de création d'un token JWT."""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert token is not None
    assert len(token) > 0
    assert isinstance(token, str)


def test_create_access_token_with_expiry():
    """Test de création d'un token JWT avec expiration personnalisée."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=60)

    token = create_access_token(data, expires_delta)

    assert token is not None
    assert len(token) > 0


def test_verify_valid_token():
    """Test de vérification d'un token valide."""
    username = "testuser"
    data = {"sub": username}
    token = create_access_token(data)

    decoded_username = verify_token(token)

    assert decoded_username == username


def test_verify_invalid_token():
    """Test de vérification d'un token invalide."""
    invalid_token = "invalid.token.here"

    result = verify_token(invalid_token)

    assert result is None


def test_verify_token_missing_subject():
    """Test de vérification d'un token sans subject."""
    # Créer un token sans 'sub'
    data = {"user": "testuser"}  # Pas de 'sub'
    token = create_access_token(data)

    result = verify_token(token)

    assert result is None


def test_token_roundtrip():
    """Test complet de création et vérification de token."""
    usernames = ["user1", "user2", "user_with_numbers123", "user-with-dashes"]

    for username in usernames:
        # Créer le token
        data = {"sub": username}
        token = create_access_token(data)

        # Vérifier le token
        decoded_username = verify_token(token)

        assert decoded_username == username


def test_empty_password():
    """Test avec un mot de passe vide."""
    password = ""
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True
    assert verify_password("notempty", hashed) is False


def test_long_password():
    """Test avec un mot de passe très long."""
    password = "a" * 1000  # 1000 caractères
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_special_characters_password():
    """Test avec un mot de passe contenant des caractères spéciaux."""
    password = "p@$$w0rd!#&*()[]{}|\\:;\"'<>,.?/~`"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_unicode_password():
    """Test avec un mot de passe contenant des caractères Unicode."""
    password = "motdepasse123éàü中文🔒"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True
    assert verify_password("motdepasse123", hashed) is False
