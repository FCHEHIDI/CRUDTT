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

### Outils

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/v1/tools/` | Liste avec filtres, tri, pagination |
| `GET` | `/api/v1/tools/{id}` | Détail complet + métriques d'usage |
| `POST` | `/api/v1/tools/` | Création d'un nouvel outil |
| `PUT` | `/api/v1/tools/{id}` | Mise à jour partielle |
| `GET` | `/health` | Vérification état de l'application |

### Analytics

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/v1/analytics/department-costs` | Coûts agrégés par département |
| `GET` | `/api/v1/analytics/expensive-tools` | Top outils les plus coûteux avec rating d'efficacité |
| `GET` | `/api/v1/analytics/tools-by-category` | Répartition outils et coûts par catégorie |
| `GET` | `/api/v1/analytics/low-usage-tools` | Outils sous-utilisés avec niveau d'alerte |
| `GET` | `/api/v1/analytics/vendor-summary` | Synthèse fournisseurs avec efficacité vendor |

### Filtres disponibles — Outils (`GET /api/v1/tools/`)

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

### Filtres disponibles — Analytics

#### `GET /api/v1/analytics/department-costs`

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `sort_by` | string | `total_cost` | `total_cost` \| `department` |
| `order` | string | `desc` | `asc` \| `desc` |

#### `GET /api/v1/analytics/expensive-tools`

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `limit` | int | `10` | Nombre de résultats (1–100) |
| `min_cost` | float | — | Filtre coût mensuel minimum |

#### `GET /api/v1/analytics/low-usage-tools`

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `max_users` | int | `5` | Seuil d'utilisateurs actifs (≥ 0) |

---

## Analytics — Logique métier

Tous les endpoints analytics portent **exclusivement sur les outils `status=active`**.

### Ratings d'efficacité outil (`efficiency_rating`)

Basé sur le ratio `cost_per_user` de l'outil vs la moyenne entreprise pondérée :

| Rating | Condition |
|--------|-----------|
| `excellent` | cpu < 50 % de la moyenne |
| `good` | 50 % ≤ cpu < 80 % |
| `average` | 80 % ≤ cpu ≤ 120 % |
| `low` | cpu > 120 % ou 0 utilisateurs |

### Niveau d'alerte outil sous-utilisé (`warning_level`)

| Niveau | Condition |
|--------|-----------|
| `high` | 0 utilisateurs **ou** cost/user > 50 € |
| `medium` | 20 € ≤ cost/user ≤ 50 € |
| `low` | cost/user < 20 € |

### Efficacité fournisseur (`vendor_efficiency`)

| Rating | `average_cost_per_user` |
|--------|-------------------------|
| `excellent` | < 5 € |
| `good` | 5 – 15 € |
| `average` | 15 – 25 € |
| `poor` | > 25 € |

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
│   │   └── tool.py             # ORM Tool + enums Python
│   ├── schemas/
│   │   ├── tool.py             # ToolCreate, ToolUpdate, ToolRead, ToolDetail
│   │   └── analytics.py        # 5 modèles de réponse Pydantic (analytics)
│   ├── services/
│   │   ├── tool.py             # Logique métier (filtres, calcul coût total, métriques)
│   │   └── analytics.py        # AnalyticsService — 5 méthodes + helpers métier
│   └── api/v1/
│       ├── endpoints/
│       │   ├── tool.py         # Handlers HTTP (codes retour, 409/404/400)
│       │   └── analytics.py    # Handlers analytics (Query validation, model_validate)
│       └── routers/
│           ├── tool.py         # Wiring routes + metadata Swagger
│           └── analytics.py    # Wiring analytics + descriptions Swagger
│
├── database/
│   ├── docker-compose.yml      # Profiles mysql / postgres
│   ├── .env                    # Port Docker (5433)
│   └── postgresql/
│       └── init.sql            # Schéma + données de démo (20 outils, 25 employés)
│
└── tests/
    ├── conftest.py             # Fixtures SQLite + override get_db
    └── test_tool.py            # 31 tests (liste, détail, création, mise à jour)
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

