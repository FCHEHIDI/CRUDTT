# CRUDTT

Projet FastAPI généré par **Fares Toolbox**.

## Démarrage rapide

```bash
# Activer le venv
source venv/bin/activate   # Linux/Mac
venv\\Scripts\\activate      # Windows

# Lancer le serveur
uvicorn app.main:app --reload --port 8000

# Lancer les tests
pytest
```

## Arborescence

```
app/
├── main.py        # Point d'entrée FastAPI
├── config.py      # Settings via pydantic-settings
├── database.py    # Session SQLAlchemy
├── models/        # Modèles ORM
├── schemas/       # Schémas Pydantic
├── routers/       # Endpoints / routes
├── services/      # Logique métier
└── utils/         # Helpers
```
