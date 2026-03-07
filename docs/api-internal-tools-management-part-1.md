# API INTERNAL TOOLS MANAGEMENT - Part 1

# **📋 TEST TECHNIQUE - API INTERNAL TOOLS MANAGEMENT**

**⏱️ Durée :** 1 journée (8h)\n**🎯 Objectif :** Développer une API REST pour la gestion des outils SaaS internes\n**💻 Stack :** Libre choix  

**📋 Livrable :** API fonctionnelle + Documentation technique



---

## **TABLE DES MATIÈRES**


1. [Vue d'ensemble](#1-vue-densemble)
2. [Contexte Business](#2-contexte-business)
3. [Spécifications Techniques](#3-sp%C3%A9cifications-techniques)
4. [Format et Présentation](#4-format-et-pr%C3%A9sentation)
5. [Modalités de Remise](#5-modalit%C3%A9s-de-remise)
6. [Critères d'Évaluation](#6-crit%C3%A8res-d%C3%A9valuation)


---

## **1. VUE D'ENSEMBLE**

### **1.1 Contexte Métier**

Vous travaillez pour **TechCorp Solutions**, une scale-up de 150 employés utilisant 20+ outils SaaS (Slack, GitHub, Figma, HubSpot...).

**Problématiques actuelles :**

* Gestion manuelle des accès outils → erreurs et perte de temps
* Visibilité limitée sur les coûts et l'usage réel
* Processus d'onboarding nouveaux employés inefficace
* Compliance et sécurité difficiles à auditer

**Votre mission :** Créer l'API backend qui alimentera la future plateforme de gestion des outils internes.

### **1.2 Objectif du Test**

Évaluer vos compétences en **développement d'APIs robustes** : compréhension business → endpoints REST → validation → persistance ORM.


---

## **2. CONTEXTE BUSINESS**

### **2.1 Personas & User Stories**

**👤 Sarah Chen (IT Manager)**\n*"J'ai besoin de voir tous nos outils par département pour optimiser les coûts de 15% cette année."*

**User Stories :**

* Lister tous les outils avec filtres (département, statut, coût)
* Visualiser les métriques d'usage par outil

**👤 Marcus Rodriguez (Finance Controller)**\n*"Je dois analyser les coûts détaillés de chaque outil pour les reportings trimestriels."*

**User Stories :**

* Consulter le détail complet d'un outil (coût, utilisateurs actifs)
* Exporter les données pour analyses Excel

**👤 Lisa Wang (HR Director)**\n*"Lors des recrutements, j'ajoute régulièrement de nouveaux outils au catalogue selon les besoins équipes."*

**User Stories :**

* Ajouter un nouvel outil au catalogue
* Valider les informations saisies (coût, vendor, URL...)

**👤 David Kumar (Platform Admin)**\n*"Je modifie constamment les statuts et prix des outils selon les négociations et renouvellements."*

**User Stories :**

* Mettre à jour les informations d'outils existants
* Changer les statuts (actif → deprecated)


---

## **3. SPÉCIFICATIONS TECHNIQUES**

### **3.1 Endpoints Obligatoires**

#### **3.1.1 GET /api/tools - Liste avec filtres**

```bash
// Besoin : Sarah veut filtrer les outils par critères business

GET /api/tools

GET /api/tools?department=Engineering&status=active

GET /api/tools?min_cost=10&max_cost=50&category=Development

// Réponse attendue :
{
  "data": [
    {
      "id": 1,
      "name": "Slack",
      "description": "Team messaging platform",
      "vendor": "Slack Technologies",
      "category": "Communication", 
      "monthly_cost": 8.00,
      "owner_department": "Engineering",
      "status": "active",
      "website_url": "https://slack.com",
      "active_users_count": 25,
      "created_at": "2025-05-01T09:00:00Z"
    }
  ],
  "total": 20,
  "filtered": 15,
  "filters_applied": {
    "department": "Engineering", 
    "status": "active"
  }
}
```

**Critères de validation :**

* Filtres multiples combinables
* Pagination supportée (page/limit optionnels)
* Tri par coût/nom/date supporté
* Gestion cas "aucun résultat" propre


---

#### **3.1.2 GET /api/tools/:id - Détail complet**

```bash
// Besoin : Marcus veut les détails financiers complets

GET /api/tools/5

// Réponse attendue :
{
  "id": 5,
  "name": "Confluence", 
  "description": "Team collaboration and documentation",
  "vendor": "Atlassian",
  "website_url": "https://confluence.atlassian.com",
  "category": "Development",
  "monthly_cost": 5.50,
  "owner_department": "Engineering",
  "status": "active",
  "active_users_count": 9,
  "total_monthly_cost": 49.50,
  "created_at": "2025-05-01T09:00:00Z",
  "updated_at": "2025-05-01T09:00:00Z",
  "usage_metrics": {
    "last_30_days": {
      "total_sessions": 127,
      "avg_session_minutes": 45
    }
  }
}
```

**Critères de validation :**

* ID numérique requis
* 404 si outil inexistant
* Métriques d'usage incluses
* Relations correctement chargées


---

#### **3.1.3 POST /api/tools - Création nouvel outil**

```bash
// Besoin : Lisa ajoute nouvel outil lors recrutement

POST /api/tools

Content-Type: application/json

{
  "name": "Linear",
  "description": "Issue tracking and project management",
  "vendor": "Linear", 
  "website_url": "https://linear.app",
  "category_id": 2,
  "monthly_cost": 8.00,
  "owner_department": "Engineering"
}

// Réponse attendue (201 Created) :
{
  "id": 21,
  "name": "Linear",
  "description": "Issue tracking and project management", 
  "vendor": "Linear",
  "website_url": "https://linear.app",
  "category": "Development",
  "monthly_cost": 8.00,
  "owner_department": "Engineering", 
  "status": "active",
  "active_users_count": 0,
  "created_at": "2025-08-20T14:30:00Z",
  "updated_at": "2025-08-20T14:30:00Z"
}
```

**Validations requises :**

* `name` : obligatoire, 2-100 caractères, unique
* `monthly_cost` : nombre ≥ 0, max 2 décimales
* `owner_department` : enum valide (Engineering|Sales|Marketing|HR|Finance|Operations|Design)
* `website_url` : format URL valide (si fourni)
* `category_id` : doit exister en base
* `vendor` : obligatoire, max 100 caractères


---

#### **3.1.4 PUT /api/tools/:id - Mise à jour**

```bash
// Besoin : David modifie prix suite négociation

PUT /api/tools/5

Content-Type: application/json

{
  "monthly_cost": 7.00,
  "status": "deprecated",
  "description": "Updated description after renewal"
}

// Réponse attendue (200 OK) :
{
  "id": 5,
  "name": "Confluence",
  "description": "Updated description after renewal",
  "vendor": "Atlassian", 
  "website_url": "https://confluence.atlassian.com",
  "category": "Development",
  "monthly_cost": 7.00,
  "owner_department": "Engineering",
  "status": "deprecated", 
  "active_users_count": 9,
  "created_at": "2025-05-01T09:00:00Z",
  "updated_at": "2025-08-20T15:45:00Z"
}
```

**Validations requises :**

* Outil doit exister (404 si inexistant)
* Mêmes validations que POST pour champs modifiés
* `status` : enum (active|deprecated|trial)
* Champs non fournis conservés
* `updated_at` automatiquement mis à jour


---

### **3.2 Gestion d'Erreurs Obligatoire**

#### **3.2.1 Codes HTTP Standards**

```bash
// Validation échouée

POST /api/tools (données invalides)
→ HTTP 400 Bad Request
{
  "error": "Validation failed",
  "details": {
    "name": "Name is required and must be 2-100 characters",
    "monthly_cost": "Must be a positive number", 
    "website_url": "Must be a valid URL format"
  }
}

// Ressource introuvable

GET /api/tools/999
→ HTTP 404 Not Found  
{
  "error": "Tool not found",
  "message": "Tool with ID 999 does not exist"
}

// Erreur serveur

GET /api/tools (DB indisponible)
→ HTTP 500 Internal Server Error
{
  "error": "Internal server error",
  "message": "Database connection failed"
}
```

### **3.3 Base de Données Fournie**

**Environnement Docker prêt à l'emploi :**

[back_env.zip 18884](attachments/09a65bf5-24b3-4082-a236-4779da9936f9.zip)

* **MySQL** : `docker-compose --profile mysql up -d`
* **PostgreSQL** : `docker-compose --profile postgres up -d`
* **Données réalistes** : 20 outils, 25 employés, 3 mois d'historique
* **Interface graphique** : phpMyAdmin (MySQL) / pgAdmin (PostgreSQL)


---

## **4. FORMAT ET PRÉSENTATION**

### **4.1 Documentation Obligatoire**

#### **4.1.1 Swagger/OpenAPI (Obligatoire)**

* Interface accessible via `/api/docs` ou `/docs` ou `/swagger-ui`
* Tous endpoints documentés avec exemples
* Schémas de validation visibles
* Interface testable directement
* **Format :** YAML ou JSON selon préférence

#### **4.1.2 [README.md](http://README.md) (Obligatoire)**

```markdown
# Internal Tools API

## Technologies
- Langage: [votre_choix]
- Framework: [votre_choix] 
- Base de données: MySQL/PostgreSQL (selon choix)
- Port API: [votre_port] (configurable)

## Quick Start

1. `docker-compose --profile mysql up -d` # ou postgres

2. [commandes_installation_dependances]
3. [commande_demarrage_serveur]
4. API disponible sur http://localhost:[port]
5. Documentation: http://localhost:[port]/[chemin_docs]

## Configuration
- Variables d'environnement: voir .env.example
- Configuration DB: [instructions_connexion]

## Tests  
[commande_lancement_tests] - Tests unitaires + intégration

## Architecture
- [Justification_choix_tech]
- [Structure_projet_expliquee]
```

### **4.2 Standards Techniques**

#### **4.2.1 Conventions Génériques**

* **Séparation responsabilités** : Controllers → Services → Models/ORM
* **Configuration externalisée** : Variables d'environnement pour ports, DB, etc.
* **Gestion d'erreurs centralisée** : Middleware ou classe dédiée
* **Validation inputs cohérente** : Schémas réutilisables

#### **4.2.2 Performance & Maintenabilité**

* **Base de données** : Pool de connexions approprié
* **Logs** : Messages structurés (level INFO/ERROR minimum)
* **Code** : Commentaires sur logique métier complexe
* **Dépendances** : Versions stables et justifiées


---

## **5. MODALITÉS DE REMISE**

### **5.1 Délais**

| **Livrable** | **Échéance** | **Format** |
|----|----|----|
| **Code + Documentation** | 24h après réception | Repository GitHub |
| **API fonctionnelle** | Démonstrable immédiatement | URL + instructions |


---

## **6. CRITÈRES D'ÉVALUATION**


* Compréhension Business (25%)
* Qualité Technique API (40%)
* Persistance & ORM (25%)
* Documentation (10%)

### **6.1 Conseils Stratégiques**


**⚡ Concentrez-vous sur :**

* Une API fonctionnelle qui répond aux besoins métier
* Validation robuste et gestion d'erreurs professionnelle
* Code lisible et structure maintenable

  \

**⚡ Stratégie gagnante 8h :**

* 📖 Analyse + Setup : 1h30 
* 💻 CRUD endpoints : 3h30
* 🔧 Validation + erreurs : 2h 
* 📋  Documentation : 1h

 ──────────────────────────────── 

     TOTAL : 8h réalistes

\n**🎯 Priorités par ordre d'importance :**


1. **Fonctionnel** → Tous endpoints opérationnels
2. **Robuste** → Validation + gestion d'erreurs
3. **Maintenable** → Code propre + tests
4. **Documenté** → Swagger + README utilisables


---

**💡 L'objectif : une API que l'équipe peut récupérer et faire évoluer immédiatement !**