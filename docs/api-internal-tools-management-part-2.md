# API INTERNAL TOOLS MANAGEMENT - Part 2

# **📊 TEST TECHNIQUE - API INTERNAL TOOLS MANAGEMENT - Part 2**

## **ANALYTICS & REPORTING**

**⏱️ Durée :** 1 journée (8h)\n**🎯 Objectif :** Développer les endpoints analytics pour optimiser les coûts outils\n**📋 Prérequis :** [API INTERNAL TOOLS MANAGEMENT - Part 1](/doc/api-internal-tools-management-part-1-w9KcsXYkzt) complété et fonctionnel


---

## **TABLE DES MATIÈRES**


1. [Contexte & Continuité](#1-contexte--continuit%C3%A9)
2. [Nouveaux Besoins Business](#2-nouveaux-besoins-business)
3. [Spécifications Analytics](#3-sp%C3%A9cifications-analytics)
4. [Critères d'Évaluation Spécifiques](#4-crit%C3%A8res-d%C3%A9valuation-sp%C3%A9cifiques)


---

## **1. CONTEXTE & CONTINUITÉ**

### **1.1 Prérequis Techniques**

**📋 Base de travail :** Votre API Part 1 avec :

* Base de données `tools` et `categories` opérationnelle
* Endpoints CRUD fonctionnels (/api/tools/\*)
* Documentation Swagger accessible
* **→ Voir [Part 1](/doc/api-internal-tools-management-part-1-w9KcsXYkzt) pour setup technique complet**

### **1.2 Évolution du Contexte**

Votre API TechCorp Solutions est en production depuis **3 mois**. Les données s'accumulent et la direction demande maintenant des **analytics avancés** pour optimiser les 30k€/mois de budget outils.

**Mission Part 2 :** Ajouter la couche analytics qui permettra des décisions data-driven sur l'optimisation des coûts.


---

## **2. NOUVEAUX BESOINS BUSINESS**

### **2.1 Personas & User Stories Analytics**

**👤 Jennifer Walsh (CFO) - Nouvelle stakeholder**\n*"Je dois présenter au board les ROI détaillés par département et identifier 200k€ d'économies potentielles cette année."*

**User Stories :**

* Visualiser la répartition des coûts par département et catégorie
* Identifier les outils les plus coûteux pour prioriser les négociations
* Détecter les outils sous-utilisés avec fort potentiel d'économies

**👤 Alex Thompson (IT Director) - Nouvelle stakeholder**\n*"J'ai besoin de dashboards temps réel pour piloter l'adoption des outils et optimiser notre stack technologique."*

**User Stories :**

* Analyser la répartition des outils par catégorie (Dev, Communication, etc.)
* Monitorer les dépenses par fournisseur pour les renouvellements
* Alerter sur les outils avec très peu d'utilisateurs actifs


---

## **3. SPÉCIFICATIONS ANALYTICS**

### **3.1 Endpoints Analytics Obligatoires**

#### **3.1.1 GET /api/analytics/department-costs - Répartition coûts départements**

```bash
// Besoin : Jennifer veut voir où va le budget par département

GET /api/analytics/department-costs

GET /api/analytics/department-costs?sort_by=total_cost&order=desc

// Réponse attendue :
{
  "data": [
    {
      "department": "Engineering",
      "total_cost": 890.50,
      "tools_count": 12,
      "total_users": 45,
      "average_cost_per_tool": 74.21,
      "cost_percentage": 36.2
    },
    {
      "department": "Sales", 
      "total_cost": 456.75,
      "tools_count": 6,
      "total_users": 18,
      "average_cost_per_tool": 76.13,
      "cost_percentage": 18.6
    }
  ],
  "summary": {
    "total_company_cost": 2450.80,
    "departments_count": 6,
    "most_expensive_department": "Engineering"
  }
}
```

**Critères de validation :**

* Agrégation correcte par département avec calculs de sommes et moyennes
* Pourcentages budget calculés précisément (doivent totaliser 100%)
* Tri par coût/département supporté
* Gestion départements sans outils actifs

  \

🤔 AMBIGUË: "cost_percentage" 

    💡 CLARIFICATION: cost_percentage = (département.total_cost / company.total_cost) \* 100 

     ↳ Pourcentage par rapport au budget total entreprise

     ↳ Tous les pourcentages doivent additionner à 100%

🤔 AMBIGUË: "average_cost_per_tool" 

    💡 CLARIFICATION: average_cost_per_tool = total_cost / tools_count 

     ↳ Moyenne simple des coûts outils du département 

     ↳ Arrondi à 2 décimales (74.21€)

🤔 AMBIGUË: "most_expensive_department"\n    💡 CLARIFICATION: Département avec le plus haut total_cost (pas coût/utilisateur) 

     ↳ Si égalité: ordre alphabétique du nom département


#### **3.1.2 GET /api/analytics/expensive-tools - Top outils coûteux**

```bash
// Besoin : Jennifer veut prioriser les négociations

GET /api/analytics/expensive-tools?limit=10

GET /api/analytics/expensive-tools?min_cost=50&limit=5

// Réponse attendue :
{
  "data": [
    {
      "id": 15,
      "name": "Enterprise CRM",
      "monthly_cost": 199.99,
      "active_users_count": 12,
      "cost_per_user": 16.67,
      "department": "Sales",
      "vendor": "BigCorp",
      "efficiency_rating": "low"
    }
  ],
  "analysis": {
    "total_tools_analyzed": 18,
    "avg_cost_per_user_company": 12.45,
    "potential_savings_identified": 345.50
  }
}
```

**Critères de validation :**

* Calcul cost_per_user précis avec gestion division par zéro
* Rating d'efficacité basé sur logique métier pertinente
* Tri par coût décroissant
* Filtres coût minimum supportés
* Analyse comparative vs moyenne entreprise

  \

🤔 AMBIGUË: "potential_savings_identified" 

    💡 CLARIFICATION: Somme des coûts des outils avec efficiency_rating = "low"

     ↳ Logique: outils inefficaces = économies potentielles 

     ↳ Si aucun outil "low" → potential_savings = 0

🤔 AMBIGUË: "efficiency_rating" 

    💡 CLARIFICATION: Basé sur cost_per_user vs avg_cost_per_user_company:

*       "excellent": < 50% de la moyenne 
*       "good": 50%-80% de la moyenne
*       "average": 80%-120% de la moyenne 
*       "low": > 120% de la moyenne

🤔 AMBIGUË: "avg_cost_per_user_company"  

   💡 CLARIFICATION: (Somme de tous monthly_cost) / (Somme de tous active_users_count) 

    ↳ Moyenne pondérée globale entreprise 

    ↳ Outils à 0 utilisateurs exclus du calcul


#### **3.1.3 GET /api/analytics/tools-by-category - Répartition catégories**

```bash
// Besoin : Alex veut analyser la stack tech par domaine

GET /api/analytics/tools-by-category

// Réponse attendue :
{
  "data": [
    {
      "category_name": "Development",
      "tools_count": 8,
      "total_cost": 650.00,
      "total_users": 67,
      "percentage_of_budget": 26.5,
      "average_cost_per_user": 9.70
    },
    {
      "category_name": "Communication",
      "tools_count": 5,
      "total_cost": 240.50,
      "total_users": 89, 
      "percentage_of_budget": 9.8,
      "average_cost_per_user": 2.70
    }
  ],
  "insights": {
    "most_expensive_category": "Development",
    "most_efficient_category": "Communication"
  }
}
```

**Critères de validation :**

* JOIN correct entre tables tools et categories
* Agrégations multiples par catégorie
* Pourcentages budget cohérents (additionnent à 100%)
* Calculs moyennes précis avec gestion cas limites
* Insights métier pertinents (plus cher, plus efficace)

  \

🤔 AMBIGUË: "most_efficient_category" 

    💡 CLARIFICATION: Catégorie avec le plus bas average_cost_per_user 

     ↳ Si égalité: ordre alphabétique du category_name

     ↳ Catégories sans utilisateurs excluses

🤔 AMBIGUË: "percentage_of_budget" 

    💡 CLARIFICATION: (catégorie.total_cost / company.total_cost) \* 100 

     ↳ Même logique que department-costs 

     ↳ Doit additionner à 100% sur toutes catégories

🤔AMBIGUË: "total_users" 

    💡 CLARIFICATION: total_users = Somme des active_users_count par catégorie

     ↳ Pas de dédupplication utilisateurs (un user peut utiliser plusieurs outils) 

     ↳ Si catégorie a outils \[10 users, 15 users\] → total_users = 25


#### **3.1.4 GET /api/analytics/low-usage-tools - Outils sous-utilisés**

```bash
// Besoin : Jennifer veut identifier les économies potentielles

GET /api/analytics/low-usage-tools?max_users=5

// Réponse attendue :
{
  "data": [
    {
      "id": 23,
      "name": "Specialized Analytics",
      "monthly_cost": 89.99,
      "active_users_count": 2,
      "cost_per_user": 45.00,
      "department": "Marketing",
      "vendor": "SmallVendor",
      "warning_level": "high",
      "potential_action": "Consider canceling or downgrading"
    }
  ],
  "savings_analysis": {
    "total_underutilized_tools": 5,
    "potential_monthly_savings": 287.50,
    "potential_annual_savings": 3450.00
  }
}
```

**Critères de validation :**

* Logique warning_level basée sur ratio usage/coût
* Actions recommandées contextualisées et pertinentes
* Calculs économies potentielles réalistes
* Filtres par seuil utilisateurs fonctionnels
* Métriques d'analyse globale des économies

  \

🤔 AMBIGUË: "total_underutilized_tools" 

    💡 CLARIFICATION: Nombre d'outils avec active_users_count <= max_users (paramètre)

     ↳ Si pas de paramètre max_users: défaut = 5 utilisateurs 

     ↳ Outils à 0 utilisateurs toujours inclus

🤔 AMBIGUË: "warning_level" 

    💡 CLARIFICATION: Basé sur cost_per_user: 

* "low": cost_per_user < 20€ 
* "medium": cost_per_user 20-50€
*  "high": cost_per_user > 50€ 

    ↳ Outils à 0 utilisateurs = "high" automatiquement

🤔 AMBIGUË: "potential_action" 

    💡 CLARIFICATION: Actions suggérées par warning_level: 

* "high": "Consider canceling or downgrading" 
* "medium": "Review usage and consider optimization"
*  "low": "Monitor usage trends"

🤔 AMBIGUË: "potential_monthly_savings" 

    💡 CLARIFICATION: Somme des monthly_cost des outils "high" + "medium" warning 

     ↳ Hypothèse: ces outils pourraient être annulés/réduits 

     ↳ potential_annual_savings = potential_monthly_savings \* 12


---

#### **3.1.5 GET /api/analytics/vendor-summary - Analyse fournisseurs**

```bash
// Besoin : Alex veut optimiser les relations vendors

GET /api/analytics/vendor-summary

// Réponse attendue :
{
  "data": [
    {
      "vendor": "Google",
      "tools_count": 4,
      "total_monthly_cost": 234.50,
      "total_users": 67,
      "departments": "Engineering,Sales,Marketing",
      "average_cost_per_user": 3.50,
      "vendor_efficiency": "excellent"
    }
  ],
  "vendor_insights": {
    "most_expensive_vendor": "BigCorp",
    "most_efficient_vendor": "Google",
    "single_tool_vendors": 8
  }
}
```

**Critères de validation :**

* Agrégation multi-niveaux par vendor
* Concaténation départements correcte
* Rating d'efficacité vendor basé sur métriques pertinentes
* Insights comparatifs entre vendors
* Détection opportunités de consolidation

  \

🤔 AMBIGUË: "single_tool_vendors" 

    💡 CLARIFICATION: Nombre de vendors qui fournissent exactement 1 outil actif 

     ↳ Statut "active" uniquement (pas maintenance/deprecated) 

     ↳ Logique: opportunité de consolidation vendors

🤔 AMBIGUË: "departments" 

    💡 CLARIFICATION: Concaténation des départements uniques, séparés par virgules 

     ↳ Ordre alphabétique: "Engineering,Marketing,Sales" 

     ↳ Pas de doublons même si vendor a plusieurs outils/département

🤔 AMBIGUË: "vendor_efficiency"\n    💡 CLARIFICATION: Basé sur average_cost_per_user du vendor: 

* "excellent": < 5€/utilisateur 
* "good": 5-15€/utilisateur
* "average": 15-25€/utilisateur
* "poor": > 25€/utilisateur

🤔 AMBIGUË: "most_efficient_vendor" 

    💡 CLARIFICATION: Vendor avec le plus bas average_cost_per_user global 

     ↳ Si égalité: ordre alphabétique du nom vendor 

     ↳ Vendors sans utilisateurs actifs exclus


---

#### **Clarification et règle globales**

🤔 AMBIGUË: Outils non-"active" 

    💡 CLARIFICATION GLOBALE: Tous les analytics incluent UNIQUEMENT les outils avec status = "active" 

     ↳ Statuts "maintenance", "deprecated", "inactive" exclus de tous les calculs 

     ↳ Exception: si endpoint spécifique le demande

**🔢 Précisions & Arrondis :**

* Montants: 2 décimales max (89.99€)
* Pourcentages: 1 décimale max (36.2%)
* Moyennes: 2 décimales max (16.67€/user)
* Somme des pourcentages: tolérance ±0.1%

**📋 Filtrage Statuts :**

Sauf mention contraire, tous les calculs incluent uniquement les outils avec `status = 'active'`


---

### **3.2 Gestion d'Erreurs Analytics**

**→ Même approche que [Part 1](/doc/api-internal-tools-management-part-1-w9KcsXYkzt) - Section 3.2** pour les codes HTTP standards, avec spécificités analytics :

```javascript
// Pas de données pour analytics

GET /api/analytics/department-costs (DB vide)
→ HTTP 200 OK
{
  "data": [],
  "message": "No analytics data available - ensure tools data exists",
  "summary": { "total_company_cost": 0 }
}

// Paramètres analytics invalides

GET /api/analytics/expensive-tools?limit=-5
→ HTTP 400 Bad Request
{
  "error": "Invalid analytics parameter",
  "details": {
    "limit": "Must be positive integer between 1 and 100"
  }
}
```


---

## **4. CRITÈRES D'ÉVALUATION SPÉCIFIQUES**

### **4.1 Pondération Part 2**

* **Compréhension Business Analytics (25%)**
* **Maîtrise SQL & Calculs Métier (50%)**
* **Architecture API Analytics (15%)**
* **Documentation Analytics (10%)**

### **4.2 Points d'Attention Spécifiques**

**🔥 SQL & Calculs :**

* Gestion division par zéro et cas limites
* Précision des calculs décimaux
* Performances requêtes avec agrégations complexes
* Logique métier traduite en SQL

**🔥 Business Logic :**

* Pourcentages cohérents et exploitables
* Ratings/recommendations basés sur données réelles
* Métriques utiles pour décisions business
* Insights permettant l'action

### **4.3 Setup & Documentation**

**→ Référez-vous à [Part 1 - Section 4](/doc/api-internal-tools-management-part-1-w9KcsXYkzt)** pour :

* Conventions Docker & base de données
* Standards README.md et Swagger
* Format de livraison
* Modalités de remise

**Ajouts spécifiques Part 2 :**

* Section explicative approche analytics dans README
* Endpoints analytics intégrés dans Swagger existant
* Tests des calculs métier et edge cases