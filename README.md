# 📋 Task Management API

Une API REST moderne de gestion de tâches développée avec FastAPI, implémentant progressivement une architecture hexagonale avec les meilleures pratiques de développement Python.

## 🎯 Objectifs du Projet

Ce projet a été conçu pour :

- **Apprendre l'architecture hexagonale** de manière progressive
- **Implémenter les bonnes pratiques** de développement Python moderne
- **Utiliser des outils professionnels** (uv, ruff, mypy, pytest)
- **Créer une API complète** avec authentification et gestion multi-utilisateurs
- **Maintenir une couverture de tests élevée** à chaque étape

## 🏗️ Architecture Évolutive

Le projet évolue en 6 phases, de l'implémentation simple vers l'architecture hexagonale :

1. **Structure Simple** : API FastAPI classique
2. **Persistance** : Intégration base de données
3. **Préparation** : Séparation des couches
4. **Architecture Hexagonale** : Migration complète
5. **Fonctionnalités Avancées** : Enrichissement métier
6. **Production Ready** : Optimisation et déploiement

## 🚀 Démarrage Rapide

```bash
# Installation avec uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Installation des dépendances
uv pip install -r requirements.txt

# Lancement de l'API
uvicorn src.main:app --reload

# Exécution des tests
pytest
```

## 🛠️ Stack Technique

### Outils de Développement
- **uv** : Gestionnaire de paquets ultra-rapide
- **ruff** : Linter et formatter
- **mypy** : Vérification de types
- **pre-commit** : Hooks de qualité

### Framework et Base de Données
- **FastAPI** : Framework web moderne
- **SQLAlchemy** : ORM avec support async
- **Alembic** : Migrations de base de données
- **SQLite → PostgreSQL** : Migration progressive

### Authentification et Sécurité
- **JWT** : Tokens d'authentification
- **bcrypt** : Hashage des mots de passe
- **OAuth2** : Standard de sécurité

### Tests
- **pytest** : Framework de tests
- **pytest-asyncio** : Support async
- **httpx** : Client HTTP de test
- **factory-boy** : Génération de données

## 📋 Roadmap et Suivi

### Phase 1 : Setup Initial et Structure Simple
- [ ] **Configuration de l'environnement**
  - [ ] Initialisation du projet avec `uv`
  - [ ] Configuration de `pyproject.toml`
  - [ ] Setup de `ruff` pour le linting et formatting
  - [ ] Configuration de `mypy` pour le typage statique
  - [ ] Setup de `pytest` pour les tests
  - [ ] Configuration de `pre-commit` hooks
  - [ ] Structure de dossiers initiale

- [ ] **API FastAPI basique**
  - [ ] Modèles Pydantic pour les tâches (`Task`, `CreateTask`, `UpdateTask`)
  - [ ] Endpoints CRUD basiques (GET, POST, PUT, DELETE)
  - [ ] Stockage en mémoire avec une liste/dictionnaire
  - [ ] Documentation automatique Swagger
  - [ ] Gestion basique des erreurs

- [ ] **Authentification basique**
  - [ ] Modèle utilisateur (`User`, `CreateUser`, `LoginUser`)
  - [ ] Endpoints d'authentification (register, login)
  - [ ] JWT tokens et middleware d'authentification
  - [ ] Protection des endpoints de tâches

- [ ] **Tests unitaires de base**
  - [ ] Tests pour chaque endpoint
  - [ ] Tests de validation des modèles Pydantic
  - [ ] Tests d'authentification
  - [ ] Configuration pytest avec fixtures
  - [ ] Tests de cas d'erreur

### Phase 2 : Amélioration et Persistance
- [ ] **Base de données**
  - [ ] Intégration SQLAlchemy avec SQLite
  - [ ] Modèles SQLAlchemy pour User et Task
  - [ ] Relations User ↔ Task (one-to-many)
  - [ ] Migrations avec Alembic
  - [ ] Configuration de la base de données

- [ ] **Couche de service simple**
  - [ ] Création des classes `UserService` et `TaskService`
  - [ ] Logique métier basique (validation, règles)
  - [ ] Gestion des permissions (user can only access own tasks)
  - [ ] Séparation des responsabilités

- [ ] **Tests avec base de données**
  - [ ] Tests d'intégration avec DB de test
  - [ ] Fixtures pour les données utilisateur/tâches
  - [ ] Tests de rollback des transactions
  - [ ] Tests des relations et permissions

### Phase 3 : Préparation à l'Architecture Hexagonale
- [ ] **Refactoring vers les interfaces**
  - [ ] Création d'interfaces abstraites (`UserRepository`, `TaskRepository`, `AuthService`)
  - [ ] Implémentation concrète SQLAlchemy
  - [ ] Injection de dépendances avec FastAPI

- [ ] **Séparation des couches**
  - [ ] Couche de présentation (routers FastAPI)
  - [ ] Couche de service (logique métier)
  - [ ] Couche de persistance (repositories)
  - [ ] Couche d'authentification

- [ ] **Tests avec mocks**
  - [ ] Tests unitaires avec mock des repositories
  - [ ] Tests d'intégration séparés
  - [ ] Coverage des tests > 90%

### Phase 4 : Migration vers Architecture Hexagonale
- [ ] **Restructuration du projet**
  ```
  src/
  ├── domain/
  │   ├── entities/          # User, Task entities
  │   ├── repositories/      # Abstract repositories
  │   ├── services/          # Domain services
  │   └── exceptions/        # Domain exceptions
  ├── application/
  │   ├── use_cases/         # Business use cases
  │   ├── dto/              # Data Transfer Objects
  │   └── interfaces/       # Application interfaces
  ├── infrastructure/
  │   ├── persistence/      # SQLAlchemy adapters
  │   ├── web/             # FastAPI adapters
  │   ├── auth/            # Auth adapters
  │   └── config/          # Configuration
  └── tests/
      ├── unit/
      ├── integration/
      └── e2e/
  ```

- [ ] **Implémentation du domaine**
  - [ ] Entités du domaine (`User`, `Task` entities)
  - [ ] Value Objects (`Email`, `TaskStatus`, `Priority`)
  - [ ] Interfaces des repositories (ports)
  - [ ] Services du domaine et règles métier
  - [ ] Exceptions du domaine

- [ ] **Couche Application**
  - [ ] Use cases (`CreateTask`, `GetUserTasks`, `UpdateTask`, `DeleteTask`)
  - [ ] Use cases d'auth (`RegisterUser`, `LoginUser`, `GetCurrentUser`)
  - [ ] DTOs pour les use cases
  - [ ] Handlers des use cases

- [ ] **Infrastructure**
  - [ ] Adaptateurs pour la persistance (SQLAlchemy)
  - [ ] Adaptateurs pour l'API web (FastAPI)
  - [ ] Adaptateurs pour l'authentification (JWT)
  - [ ] Configuration et injection de dépendances

### Phase 5 : Fonctionnalités Avancées
- [ ] **Fonctionnalités métier**
  - [ ] Statuts des tâches (TODO, IN_PROGRESS, DONE, CANCELLED)
  - [ ] Priorités des tâches (LOW, MEDIUM, HIGH, URGENT)
  - [ ] Dates d'échéance et rappels
  - [ ] Catégories/Tags pour organiser les tâches
  - [ ] Assignation de tâches entre utilisateurs

- [ ] **Validation et règles métier**
  - [ ] Validation des transitions d'état
  - [ ] Règles de priorité et d'escalade
  - [ ] Contraintes de dates (échéance > création)
  - [ ] Limites par utilisateur (quotas)

- [ ] **API avancée**
  - [ ] Filtres complexes (statut, priorité, date, catégorie)
  - [ ] Tri et pagination
  - [ ] Recherche full-text dans les tâches
  - [ ] Statistiques utilisateur

- [ ] **Tests complets**
  - [ ] Tests des use cases complexes
  - [ ] Tests des entités et value objects
  - [ ] Tests des adaptateurs
  - [ ] Tests end-to-end avec scénarios complets

### Phase 6 : Optimisation et Production
- [ ] **Performance**
  - [ ] Pagination efficace avec curseurs
  - [ ] Index de base de données optimisés
  - [ ] Cache Redis pour les données fréquentes
  - [ ] Optimisation des requêtes N+1

- [ ] **Migration PostgreSQL**
  - [ ] Configuration PostgreSQL
  - [ ] Migration des données SQLite → PostgreSQL
  - [ ] Optimisations spécifiques PostgreSQL
  - [ ] Connection pooling

- [ ] **Observabilité**
  - [ ] Logging structuré avec contexte utilisateur
  - [ ] Métriques Prometheus (optionnel)
  - [ ] Health checks détaillés
  - [ ] Monitoring des performances

- [ ] **Déploiement**
  - [ ] Dockerfile optimisé multi-stage
  - [ ] docker-compose pour développement et prod
  - [ ] Variables d'environnement sécurisées
  - [ ] CI/CD avec GitHub Actions
  - [ ] Tests automatisés en CI

## 📁 Structure du Projet

```
task-management-api/
├── src/                    # Code source
├── tests/                  # Tests
├── alembic/               # Migrations de base de données
├── docs/                  # Documentation
├── scripts/               # Scripts utilitaires
├── .github/               # GitHub Actions
├── pyproject.toml         # Configuration du projet
├── requirements.txt       # Dépendances
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```

## 🧪 Tests

```bash
# Tous les tests
pytest

# Tests avec coverage
pytest --cov=src --cov-report=html

# Tests d'un module spécifique
pytest tests/test_tasks.py

# Tests en mode verbose
pytest -v
```

## 🔧 Développement

```bash
# Setup pre-commit hooks
pre-commit install

# Linting et formatting
ruff check src/
ruff format src/

# Vérification de types
mypy src/

# Nouvelles migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📚 Documentation

- **API Documentation** : `/docs` (Swagger UI)
- **Alternative Documentation** : `/redoc` (ReDoc)
- **Architecture Decision Records** : `docs/adr/`
- **Development Guide** : `docs/development.md`

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## ✅ Statut Actuel

**Phase en cours** : Phase 1 - Setup Initial et Structure Simple  
**Progression globale** : 0% ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜

---

*Ce README sera mis à jour au fur et à mesure de l'avancement du projet.*