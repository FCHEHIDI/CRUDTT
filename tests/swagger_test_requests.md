# Requêtes de test — Swagger UI
# http://localhost:8000/docs

## Contexte DB
# Catégories dispo : 1=Communication, 2=Development, 3=Design, 4=Productivity,
#                    5=Analytics, 6=Security, 7=Marketing, 8=HR, 9=Finance, 10=Infrastructure
# Outils existants  : 1=Slack, 2=Zoom, 3=GitHub, 4=Jira, 5=Confluence, 6=Docker Hub

---

## 1. GET /api/v1/tools/ — Liste tous les outils
Pas de body.

---

## 2. GET /api/v1/tools/ — Filtrer par département
Query params :
  department = Engineering

---

## 3. GET /api/v1/tools/ — Filtrer par statut + tri par coût
Query params :
  status   = active
  sort_by  = monthly_cost
  order    = desc

---

## 4. GET /api/v1/tools/ — Filtrer par catégorie + pagination
Query params :
  category = Development
  page     = 1
  limit    = 5

---

## 5. GET /api/v1/tools/ — Filtrer par fourchette de coût
Query params :
  min_cost = 10
  max_cost = 100

---

## 6. GET /api/v1/tools/{tool_id} — Détail d'un outil existant
Path param : tool_id = 1

---

## 7. GET /api/v1/tools/{tool_id} — Outil inexistant → 404
Path param : tool_id = 9999

---

## 8. POST /api/v1/tools/ — Créer un outil valide → 201
Body :
{
  "name": "Sentry",
  "vendor": "Functional Software Inc.",
  "description": "Outil de monitoring et tracking d'erreurs",
  "website_url": "https://sentry.io",
  "category_id": 6,
  "monthly_cost": 29.00,
  "owner_department": "Engineering"
}

---

## 9. POST /api/v1/tools/ — Créer sans champs optionnels → 201
Body :
{
  "name": "Linear",
  "vendor": "Linear",
  "category_id": 2,
  "monthly_cost": 8.00,
  "owner_department": "Engineering"
}

---

## 10. POST /api/v1/tools/ — Nom déjà existant → 409
Body :
{
  "name": "Slack",
  "vendor": "Salesforce",
  "category_id": 1,
  "monthly_cost": 12.50,
  "owner_department": "Engineering"
}

---

## 11. POST /api/v1/tools/ — Catégorie inexistante → 400
Body :
{
  "name": "Ghost Tool",
  "vendor": "Acme",
  "category_id": 9999,
  "monthly_cost": 5.00,
  "owner_department": "HR"
}

---

## 12. POST /api/v1/tools/ — URL invalide → 400
Body :
{
  "name": "Bad URL Tool",
  "vendor": "Acme",
  "category_id": 1,
  "monthly_cost": 5.00,
  "owner_department": "HR",
  "website_url": "slack.com"
}

---

## 13. POST /api/v1/tools/ — Champ obligatoire manquant → 400
Body :
{
  "name": "Incomplete Tool"
}

---

## 14. PUT /api/v1/tools/{tool_id} — Changer le statut → deprecated
Path param : tool_id = 6
Body :
{
  "status": "deprecated"
}

---

## 15. PUT /api/v1/tools/{tool_id} — Mise à jour partielle (nom + coût)
Path param : tool_id = 2
Body :
{
  "name": "Zoom Pro",
  "monthly_cost": 25.00
}

---

## 16. PUT /api/v1/tools/{tool_id} — Changer de catégorie
Path param : tool_id = 3
Body :
{
  "category_id": 6
}

---

## 17. PUT /api/v1/tools/{tool_id} — Outil inexistant → 404
Path param : tool_id = 9999
Body :
{
  "name": "Ghost"
}

---

## 18. PUT /api/v1/tools/{tool_id} — Catégorie invalide → 400
Path param : tool_id = 1
Body :
{
  "category_id": 9999
}
