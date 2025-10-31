# Sentry-AI : Plan de Projet et Architecture

**Version:** 1.0
**Date:** 31 Octobre 2025
**Auteur:** Manus AI

---

## 1. Introduction et Vision du Projet

### 1.1. Contexte

Le projet **Sentry-AI** vise à développer un agent d'automatisation cognitive pour l'écosystème macOS. Cet agent a pour mission d'observer l'environnement de l'utilisateur, de comprendre le contexte des interactions (en particulier les boîtes de dialogue et les notifications), de prendre des décisions éclairées grâce à une intelligence artificielle locale, et d'agir en conséquence pour automatiser les tâches répétitives. L'objectif est de créer un assistant proactif qui fluidifie le travail de l'utilisateur sans compromettre la sécurité ni la confidentialité.

### 1.2. Inspiration et Méthodologie

Ce projet s'inspire de la structure professionnelle et de la méthodologie de développement du projet **Yago**. Nous adopterons une approche similaire en matière de documentation, de structure de code, de tests et de gestion de projet pour garantir un résultat robuste, maintenable et évolutif.

### 1.3. Objectifs Clés

*   **Automatisation Intelligente :** Aller au-delà des scripts traditionnels en intégrant un moteur de décision basé sur un grand modèle de langage (LLM) fonctionnant localement.
*   **Confidentialité Absolue :** Assurer que toutes les données (captures d'écran, textes, etc.) sont traitées localement sur la machine de l'utilisateur, sans jamais être envoyées vers des serveurs externes.
*   **Performance et Efficacité :** Optimiser l'agent pour qu'il ait un impact minimal sur les ressources système (CPU, batterie) en utilisant les API natives de macOS et les capacités d'Apple Silicon.
*   **Transparence et Contrôle :** Fournir à l'utilisateur un contrôle total sur les actions de l'agent, avec des journaux clairs et la possibilité de définir des règles personnalisées.

---

## 2. Architecture Technique

L'architecture de Sentry-AI est conçue pour être modulaire, résiliente et sécurisée. Elle s'articule autour de quatre services principaux fonctionnant en arrière-plan.

![Architecture Diagram](architecture.png)  <!-- Placeholder for diagram -->

### 2.1. Composants de l'Architecture

| Composant | Technologie | Rôle et Responsabilités |
| :--- | :--- | :--- |
| **Observer (Gözlemci)** | Python + `pyobjc` (Accessibility API) | - Surveille en permanence l'état de l'interface utilisateur.<br>- Détecte l'apparition de nouvelles fenêtres ou boîtes de dialogue.<br>- Utilise l'API d'accessibilité pour extraire la hiérarchie des éléments UI (texte, boutons, etc.) de manière structurée. |
| **Analyzer (Analizci)** | Python + Apple Vision Framework | - Reçoit les données brutes de l'Observer.<br>- Analyse le contenu textuel et la structure de la boîte de dialogue pour en extraire le contexte (application, question posée, options disponibles).<br>- En cas d'échec de l'API d'accessibilité (pour les applications non natives), effectue une capture d'écran et utilise l'OCR du Vision Framework comme solution de repli. |
| **Decision Engine (Karar Verici)** | Python + Ollama (local LLM) | - Reçoit le contexte de l'Analyzer.<br>- Construit un prompt détaillé et l'envoie à un LLM local (ex: Phi-3, Llama 3) via Ollama.<br>- Reçoit la décision de l'IA (ex: "Cliquer sur 'Enregistrer'") et la valide par rapport aux options disponibles. |
| **Actor (Eylemci)** | Python + `pyobjc` (Accessibility API) | - Reçoit la décision validée du Decision Engine.<br>- Identifie l'élément UI correspondant (le bouton) dans la hiérarchie fournie par l'Observer.<br>- Exécute l'action de manière programmatique (`kAXPressAction`) pour simuler le clic de l'utilisateur. |
| **Core Service** | Python (FastAPI) | - Orchestre le flux de données entre les différents modules.<br>- Gère la configuration, les logs et l'état global de l'agent.<br>- Expose une API locale pour une éventuelle interface utilisateur. |

### 2.2. Flux de Données

1.  L'**Observer** détecte une nouvelle boîte de dialogue et envoie la hiérarchie des éléments UI au **Core Service**.
2.  Le **Core Service** transmet ces informations à l'**Analyzer**.
3.  L'**Analyzer** extrait le contexte. Si nécessaire, il demande une capture d'écran au **Core Service** pour analyse OCR.
4.  L'**Analyzer** renvoie le contexte structuré (question, options, application) au **Core Service**.
5.  Le **Core Service** passe ce contexte au **Decision Engine**.
6.  Le **Decision Engine** interroge le LLM local et renvoie la décision (ex: "Enregistrer") au **Core Service**.
7.  Le **Core Service** valide la décision et la transmet à l'**Actor** avec la référence de l'élément UI.
8.  L'**Actor** exécute le clic et notifie le succès au **Core Service**, qui enregistre l'action dans les logs.

---

## 3. Stack Technologique

La stack est choisie pour privilégier la performance, l'intégration native à macOS et la sécurité.

*   **Langage Principal :** Python 3.11+
*   **Intégration macOS :** `pyobjc` pour un accès direct aux frameworks natifs (Accessibility, Vision).
*   **IA Locale :** Ollama pour la gestion et l'exécution des LLMs. Le modèle initial sera `phi3:mini` pour sa légèreté et sa rapidité.
*   **Service Core :** FastAPI pour créer une API interne robuste et asynchrone.
*   **Base de Données :** SQLite pour le stockage local des logs, des configurations et des préférences.
*   **Tests :** `pytest` pour les tests unitaires et d'intégration.
*   **Packaging :** `py2app` pour créer une application macOS autonome.

---

## 4. Structure du Projet (Inspirée de Yago)

Le projet sera organisé dans une structure claire pour faciliter la navigation et la maintenance.

```
/Sentry-AI
├── .github/              # Workflows CI/CD
├── .gitignore
├── LICENSE
├── PROJECT_PLAN.md       # Ce document
├── README.md             # Documentation principale
├── docs/
│   ├── architecture.md
│   └── api.md
├── requirements.txt
├── sentry_ai/            # Code source principal
│   ├── __init__.py
│   ├── main.py             # Point d'entrée de l'application
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── orchestrator.py # Core Service
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── observer.py
│   │   ├── analyzer.py
│   │   ├── decision_engine.py
│   │   └── actor.py
│   ├── api/
│   │   └── routes.py       # Endpoints FastAPI
│   ├── models/
│   │   └── data_models.py  # Modèles Pydantic
│   └── utils/
│       └── logger.py
└── tests/
    ├── __init__.py
    ├── test_agents.py
    └── test_core.py
```

---

## 5. Feuille de Route (Roadmap)

### Milestone 1 : Fondations et Preuve de Concept (PoC)

*   **Objectif :** Mettre en place la structure du projet et valider le flux de base avec une application cible (ex: TextEdit).
*   **Tâches :**
    1.  Initialiser le dépôt Git avec la structure de dossiers.
    2.  Développer le module **Observer** pour détecter les boîtes de dialogue de TextEdit.
    3.  Implémenter une version simple de l'**Analyzer**.
    4.  Intégrer le **Decision Engine** avec Ollama.
    5.  Développer le module **Actor** pour cliquer sur "Enregistrer" ou "Ne pas enregistrer".
    6.  Rédiger les tests unitaires pour chaque module.

### Milestone 2 : Robustesse et Fiabilité

*   **Objectif :** Améliorer la gestion des erreurs, la compatibilité et la performance.
*   **Tâches :**
    1.  Implémenter la logique de fallback OCR avec le Vision Framework.
    2.  Mettre en place un système de logs complet avec SQLite.
    3.  Créer une liste blanche/noire d'applications pour des raisons de sécurité.
    4.  Optimiser la consommation CPU en passant à une approche plus événementielle.

### Milestone 3 : Interface Utilisateur et Configuration

*   **Objectif :** Donner à l'utilisateur la visibilité et le contrôle sur l'agent.
*   **Tâches :**
    1.  Développer une interface utilisateur simple (peut-être une application de barre de menus) en utilisant `rumps` (Python) ou SwiftUI.
    2.  Afficher les logs des actions en temps réel.
    3.  Permettre à l'utilisateur d'activer/désactiver l'agent.
    4.  Permettre la configuration de la liste blanche/noire.

---

## 6. Bonnes Pratiques

*   **Gestion de Version :** Suivre les conventions de `Conventional Commits`.
*   **Documentation :** Maintenir le `README.md` à jour et documenter le code avec des docstrings claires.
*   **Tests :** Viser une couverture de test d'au moins 80% pour les modules critiques.
*   **Revue de Code :** Toutes les modifications devront passer par une Pull Request avec au moins un approbateur.
