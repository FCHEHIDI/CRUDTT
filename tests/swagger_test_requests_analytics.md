# Swagger / cURL — Tests manuels Analytics

Swagger UI : **http://127.0.0.1:8000/docs**  
Base URL   : **http://127.0.0.1:8000/api/v1/analytics**

---

## 1. `GET /department-costs`

### Défaut (tri par coût décroissant)
```
GET /api/v1/analytics/department-costs
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/department-costs"
```
**Attendu** : `200` — `data` trié du département le plus cher au moins cher, `cost_percentage` somме ≈ 100.

---

### Tri alphabétique croissant
```
GET /api/v1/analytics/department-costs?sort_by=department&order=asc
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/department-costs?sort_by=department&order=asc"
```
**Attendu** : `200` — départements en ordre A → Z.

---

### Tri par coût croissant
```
GET /api/v1/analytics/department-costs?sort_by=total_cost&order=asc
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/department-costs?sort_by=total_cost&order=asc"
```
**Attendu** : `200` — département le moins cher en premier.

---

## 2. `GET /expensive-tools`

### Défaut (top 10)
```
GET /api/v1/analytics/expensive-tools
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/expensive-tools"
```
**Attendu** : `200` — max 10 outils actifs, triés par `monthly_cost` desc, champ `efficiency_rating` présent.

---

### Avec limite personnalisée
```
GET /api/v1/analytics/expensive-tools?limit=3
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/expensive-tools?limit=3"
```
**Attendu** : `200` — exactement 3 outils maximum dans `data`.

---

### Avec filtre de coût minimum
```
GET /api/v1/analytics/expensive-tools?min_cost=500
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/expensive-tools?min_cost=500"
```
**Attendu** : `200` — uniquement les outils avec `monthly_cost > 500`.

---

### Combiné : limit + min_cost
```
GET /api/v1/analytics/expensive-tools?limit=5&min_cost=100
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/expensive-tools?limit=5&min_cost=100"
```
**Attendu** : `200` — max 5 outils, tous avec `monthly_cost > 100`.

---

### Validation — limit invalide (< 1)
```
GET /api/v1/analytics/expensive-tools?limit=0
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/expensive-tools?limit=0"
```
**Attendu** : `400`
```json
{
  "detail": "Please correct the following validation errors and try again.\nFor 'limit': Value must be greater than or equal to 1."
}
```

---

### Validation — limit trop grand (> 100)
```
GET /api/v1/analytics/expensive-tools?limit=200
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/expensive-tools?limit=200"
```
**Attendu** : `400`
```json
{
  "detail": "Please correct the following validation errors and try again.\nFor 'limit': Value must be less than or equal to 100."
}
```

---

### Validation — min_cost négatif
```
GET /api/v1/analytics/expensive-tools?min_cost=-10
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/expensive-tools?min_cost=-10"
```
**Attendu** : `400`
```json
{
  "detail": "Please correct the following validation errors and try again.\nFor 'min_cost': Value must be greater than 0."
}
```

---

## 3. `GET /tools-by-category`

### Défaut (aucun paramètre)
```
GET /api/v1/analytics/tools-by-category
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/tools-by-category"
```
**Attendu** : `200` — chaque entrée contient `category_name`, `tools_count`, `total_cost`, `percentage_of_budget`, `average_cost_per_user`. Somme des `percentage_of_budget` ≈ 100. `insights.most_expensive_category` et `most_efficient_category` renseignés.

---

## 4. `GET /low-usage-tools`

### Défaut (max_users = 5)
```
GET /api/v1/analytics/low-usage-tools
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/low-usage-tools"
```
**Attendu** : `200` — outils actifs avec `active_users_count ≤ 5`, champ `warning_level` parmi `high / medium / low`.

---

### Seuil personnalisé
```
GET /api/v1/analytics/low-usage-tools?max_users=2
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/low-usage-tools?max_users=2"
```
**Attendu** : `200` — uniquement les outils avec `active_users_count ≤ 2`.

---

### Outils sans aucun utilisateur
```
GET /api/v1/analytics/low-usage-tools?max_users=0
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/low-usage-tools?max_users=0"
```
**Attendu** : `200` — outils avec `active_users_count = 0`, tous avec `warning_level = "high"` et `cost_per_user = null`.

---

### Vérifier les économies estimées
```
GET /api/v1/analytics/low-usage-tools?max_users=10
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/low-usage-tools?max_users=10"
```
**Attendu** : `200` — `savings_analysis.potential_annual_savings` = `potential_monthly_savings × 12`.

---

### Validation — max_users négatif
```
GET /api/v1/analytics/low-usage-tools?max_users=-1
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/low-usage-tools?max_users=-1"
```
**Attendu** : `400`
```json
{
  "detail": "Please correct the following validation errors and try again.\nFor 'max_users': Value must be greater than or equal to 0."
}
```

---

## 5. `GET /vendor-summary`

### Défaut (aucun paramètre)
```
GET /api/v1/analytics/vendor-summary
```
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/analytics/vendor-summary"
```
**Attendu** : `200` — chaque entrée contient `vendor`, `tools_count`, `total_monthly_cost`, `average_cost_per_user`, `vendor_efficiency`, `departments`. `vendor_insights.most_expensive_vendor`, `most_efficient_vendor` et `single_tool_vendors` renseignés.

---

## Champs de référence

### `efficiency_rating` (expensive-tools)
| Ratio `cpu / avg_cpu` | Valeur |
|---|---|
| < 0.5 | `excellent` |
| 0.5 – 0.8 | `good` |
| 0.8 – 1.2 | `average` |
| > 1.2 ou 0 users | `low` |

### `warning_level` (low-usage-tools)
| Condition | Valeur |
|---|---|
| `active_users_count = 0` | `high` |
| `cost_per_user > 50` | `high` |
| `20 ≤ cost_per_user ≤ 50` | `medium` |
| `cost_per_user < 20` | `low` |

### `vendor_efficiency` (vendor-summary)
| `average_cost_per_user` | Valeur |
|---|---|
| < 5 | `excellent` |
| 5 – 15 | `good` |
| 15 – 25 | `average` |
| > 25 | `poor` |
