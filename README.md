# Internal Tools API

API REST de gestion des outils SaaS internes — développée dans le cadre du test technique **TechCorp Solutions**.

## Technologies

| Couche | Choix |
|--------|-------|
| Langage | Python 3.12 |
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Base de données | PostgreSQL 16 (Docker) |
| Migrations | Alembic |
| Tests | Pytest + SQLite in-memory |
| Port API | **8000** (configurable via `.env`) |

---

## Quick Start

### 1. Démarrer la base de données

```bash
cd database
docker compose --profile postgres up -d
cd ..
```

### 2. Installer les dépendances

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env si nécessaire (valeurs par défaut fonctionnelles avec Docker)
```

### 4. Démarrer le serveur

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur **http://localhost:8000**

Documentation interactive : **http://localhost:8000/docs**  
Documentation alternative (ReDoc) : **http://localhost:8000/redoc**

---

## Configuration

Variables d'environnement (fichier `.env`) :

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `APP_NAME` | `Internal Tools API` | Nom affiché dans Swagger |
| `APP_ENV` | `development` | Environnement |
| `DEBUG` | `True` | Mode debug FastAPI |
| `DATABASE_URL` | `postgresql://dev:dev123@localhost:5433/internal_tools` | URL de connexion PostgreSQL |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Origines CORS autorisées |

> La base de données Docker expose PostgreSQL sur le port **5433** pour éviter tout conflit avec une installation locale.

---

## Tests

```bash
pytest
```

- **38 tests** — unitaires + intégration
- Base SQLite in-memory isolée par test (aucune dépendance Docker)
- Couvre : liste/filtres, détail, création (201/400/409), mise à jour (200/400/404)

```bash
# Avec rapport de couverture détaillé
pytest -v
```

---

## Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/v1/tools/` | Liste avec filtres, tri, pagination |
| `GET` | `/api/v1/tools/{id}` | Détail complet + métriques d'usage |
| `POST` | `/api/v1/tools/` | Création d'un nouvel outil |
| `PUT` | `/api/v1/tools/{id}` | Mise à jour partielle |
| `GET` | `/health` | Vérification état de l'application |

### Filtres disponibles (`GET /api/v1/tools/`)

| Paramètre | Type | Exemple |
|-----------|------|---------|
| `department` | string | `Engineering` |
| `status` | string | `active` \| `deprecated` \| `trial` |
| `category` | string | `Development` |
| `min_cost` | float | `10.0` |
| `max_cost` | float | `100.0` |
| `sort_by` | string | `monthly_cost` \| `name` \| `created_at` |
| `order` | string | `asc` \| `desc` |
| `page` | int | `1` |
| `limit` | int | `20` |

---

## Architecture

```
CRUDTT/
├── .env                        # Variables d'environnement (non versionné)
├── .env.example                # Template de configuration
├── pytest.ini                  # Configuration pytest
├── requirements.txt
├── README.md
│
├── app/
│   ├── main.py                 # Point d'entrée, CORS, handlers d'erreurs, metadata OpenAPI
│   ├── core/
│   │   ├── config.py           # Settings via pydantic-settings (.env)
│   │   ├── database.py         # Engine SQLAlchemy, session factory
│   │   └── dependencies.py     # Injection de dépendances (get_db)
│   ├── models/
│   │   ├── category.py         # ORM Category
│   │   ├── tool.py             # ORM Tool + enums Python
│   │   └── user.py             # ORM User
│   ├── schemas/
│   │   ├── tool.py             # ToolCreate, ToolUpdate, ToolRead, ToolDetail
│   │   └── user.py
│   ├── services/
│   │   ├── tool.py             # Logique métier (filtres, calcul coût total, métriques)
│   │   └── user.py
│   └── api/v1/
│       ├── endpoints/
│       │   ├── tool.py         # Handlers HTTP (codes retour, 409/404/400)
│       │   └── user.py
│       └── routers/
│           ├── tool.py         # Wiring routes + metadata Swagger
│           └── user.py
│
├── database/
│   ├── docker-compose.yml      # Profiles mysql / postgres
│   ├── .env                    # Port Docker (5433)
│   └── postgresql/
│       └── init.sql            # Schéma + données de démo (20 outils, 25 employés)
│
└── tests/
    ├── conftest.py             # Fixtures SQLite + override get_db
    ├── test_tool.py            # 31 tests (liste, détail, création, mise à jour)
    └── test_user.py
```

**Choix d'architecture :**

- **Séparation stricte** Controllers → Services → ORM : chaque couche a une responsabilité unique
- **Pydantic v2** pour la validation des entrées avec messages d'erreur explicites
- **SQLAlchemy 2.0** avec `joinedload` pour éviter les requêtes N+1
- **String columns** (pas `Enum` SQL) pour la compatibilité avec les types PostgreSQL existants dans `init.sql`
- **Configuration externalisée** : aucune valeur sensible dans le code
- **Tests indépendants de l'infrastructure** : base SQLite créée/détruite à chaque test via `dependency_overrides` FastAPI — aucun Docker requis pour lancer la suite

---

## Gestion d'erreurs

| Code | Cas |
|------|-----|
| `400` | Validation échouée (champ manquant, URL invalide, catégorie inexistante…) |
| `404` | Outil inexistant |
| `409` | Nom d'outil déjà utilisé |
| `500` | Erreur interne (handler global) |

