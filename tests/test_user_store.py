"""Tests pour le stockage des utilisateurs."""
import pytest

from src.models.user_store import UserStore
from src.schemas.user import UserCreate


@pytest.fixture
def user_store():
    """Fixture pour un stockage d'utilisateurs vide."""
    return UserStore()


@pytest.fixture
def sample_user_data():
    """Fixture pour des données d'utilisateur exemple."""
    return UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
    )


def test_create_user_success(user_store, sample_user_data):
    """Test de création d'un utilisateur avec succès."""
    user = user_store.create_user(sample_user_data)

    assert user.id == 1
    assert user.username == sample_user_data.username
    assert user.email == sample_user_data.email
    assert user.full_name == sample_user_data.full_name
    assert user.is_active is True
    assert user.created_at is not None


def test_create_user_minimal(user_store):
    """Test de création d'un utilisateur avec les champs minimaux."""
    user_data = UserCreate(
        username="minimaluser", email="minimal@example.com", password="password123"
    )

    user = user_store.create_user(user_data)

    assert user.username == "minimaluser"
    assert user.email == "minimal@example.com"
    assert user.full_name is None
    assert user.is_active is True


def test_create_user_duplicate_username(user_store, sample_user_data):
    """Test de création avec un nom d'utilisateur déjà utilisé."""
    # Créer le premier utilisateur
    user_store.create_user(sample_user_data)

    # Essayer de créer un deuxième avec le même nom d'utilisateur
    duplicate_user = UserCreate(
        username=sample_user_data.username,
        email="different@example.com",
        password="password456",
    )

    with pytest.raises(ValueError, match="nom d'utilisateur existe déjà"):
        user_store.create_user(duplicate_user)


def test_create_user_duplicate_email(user_store, sample_user_data):
    """Test de création avec un email déjà utilisé."""
    # Créer le premier utilisateur
    user_store.create_user(sample_user_data)

    # Essayer de créer un deuxième avec le même email
    duplicate_user = UserCreate(
        username="differentuser", email=sample_user_data.email, password="password456"
    )

    with pytest.raises(ValueError, match="email existe déjà"):
        user_store.create_user(duplicate_user)


def test_get_user_by_username_exists(user_store, sample_user_data):
    """Test de récupération d'un utilisateur par nom d'utilisateur."""
    created_user = user_store.create_user(sample_user_data)
    retrieved_user = user_store.get_user_by_username(sample_user_data.username)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == created_user.username
    assert hasattr(retrieved_user, "hashed_password")  # UserInDB


def test_get_user_by_username_not_exists(user_store):
    """Test de récupération d'un utilisateur inexistant par nom d'utilisateur."""
    user = user_store.get_user_by_username("nonexistent")
    assert user is None


def test_get_user_by_email_exists(user_store, sample_user_data):
    """Test de récupération d'un utilisateur par email."""
    created_user = user_store.create_user(sample_user_data)
    retrieved_user = user_store.get_user_by_email(sample_user_data.email)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email


def test_get_user_by_email_not_exists(user_store):
    """Test de récupération d'un utilisateur inexistant par email."""
    user = user_store.get_user_by_email("nonexistent@example.com")
    assert user is None


def test_get_user_by_id_exists(user_store, sample_user_data):
    """Test de récupération d'un utilisateur par ID."""
    created_user = user_store.create_user(sample_user_data)
    retrieved_user = user_store.get_user_by_id(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == created_user.username
    assert not hasattr(retrieved_user, "hashed_password")  # User, pas UserInDB


def test_get_user_by_id_not_exists(user_store):
    """Test de récupération d'un utilisateur inexistant par ID."""
    user = user_store.get_user_by_id(999)
    assert user is None


def test_authenticate_user_success(user_store, sample_user_data):
    """Test d'authentification avec succès."""
    user_store.create_user(sample_user_data)

    authenticated_user = user_store.authenticate_user(
        sample_user_data.username, sample_user_data.password
    )

    assert authenticated_user is not None
    assert authenticated_user.username == sample_user_data.username
    assert authenticated_user.is_active is True


def test_authenticate_user_wrong_username(user_store, sample_user_data):
    """Test d'authentification avec mauvais nom d'utilisateur."""
    user_store.create_user(sample_user_data)

    authenticated_user = user_store.authenticate_user(
        "wronguser", sample_user_data.password
    )

    assert authenticated_user is None


def test_authenticate_user_wrong_password(user_store, sample_user_data):
    """Test d'authentification avec mauvais mot de passe."""
    user_store.create_user(sample_user_data)

    authenticated_user = user_store.authenticate_user(
        sample_user_data.username, "wrongpassword"
    )

    assert authenticated_user is None


def test_authenticate_inactive_user(user_store, sample_user_data):
    """Test d'authentification d'un utilisateur inactif."""
    # Créer l'utilisateur
    user_store.create_user(sample_user_data)

    # Marquer comme inactif
    user_in_db = user_store.get_user_by_username(sample_user_data.username)
    user_in_db.is_active = False

    # Essayer de s'authentifier
    authenticated_user = user_store.authenticate_user(
        sample_user_data.username, sample_user_data.password
    )

    assert authenticated_user is None


def test_password_is_hashed(user_store, sample_user_data):
    """Test que le mot de passe est bien hashé en base."""
    user_store.create_user(sample_user_data)

    user_in_db = user_store.get_user_by_username(sample_user_data.username)

    assert user_in_db.hashed_password != sample_user_data.password
    assert len(user_in_db.hashed_password) > 0


def test_multiple_users_creation(user_store):
    """Test de création de plusieurs utilisateurs."""
    users_data = [
        UserCreate(username="user1", email="user1@example.com", password="pass1"),
        UserCreate(username="user2", email="user2@example.com", password="pass2"),
        UserCreate(username="user3", email="user3@example.com", password="pass3"),
    ]

    created_users = []
    for user_data in users_data:
        user = user_store.create_user(user_data)
        created_users.append(user)

    # Vérifier les IDs
    assert created_users[0].id == 1
    assert created_users[1].id == 2
    assert created_users[2].id == 3

    # Vérifier que tous sont récupérables
    for i, user_data in enumerate(users_data):
        retrieved_user = user_store.get_user_by_username(user_data.username)
        assert retrieved_user is not None
        assert retrieved_user.id == i + 1


def test_user_store_isolation(user_store, sample_user_data):
    """Test de l'isolation entre les différentes méthodes d'accès."""
    # Créer un utilisateur
    created_user = user_store.create_user(sample_user_data)

    # Récupérer par les 3 méthodes
    by_username = user_store.get_user_by_username(sample_user_data.username)
    by_email = user_store.get_user_by_email(sample_user_data.email)
    by_id = user_store.get_user_by_id(created_user.id)

    # Vérifier la cohérence
    assert by_username.id == created_user.id
    assert by_email.id == created_user.id
    assert by_id.id == created_user.id

    # Vérifier les types
    assert hasattr(by_username, "hashed_password")  # UserInDB
    assert hasattr(by_email, "hashed_password")  # UserInDB
    assert not hasattr(by_id, "hashed_password")  # User
