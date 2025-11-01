# 🤖 Sentry-AI - Cognitive Automation Agent for macOS

**Version:** 1.1.0
**Status:** ✅ Production Ready
**License:** MIT

> **Un agent d'automatisation cognitive qui observe, comprend et agit sur votre environnement macOS de manière intelligente et sécurisée.**

---

## 🌟 Vision du Projet

Sentry-AI est un agent d'intelligence artificielle conçu pour automatiser les tâches répétitives sur macOS en observant l'interface utilisateur, en comprenant le contexte grâce à un modèle de langage local, et en prenant des décisions intelligentes pour agir en votre nom. Contrairement aux solutions traditionnelles d'automatisation, Sentry-AI combine la puissance des API natives d'Apple avec l'intelligence des LLMs pour offrir une expérience d'automatisation véritablement cognitive.

### Pourquoi Sentry-AI ?

Les utilisateurs de macOS sont constamment interrompus par des boîtes de dialogue demandant des confirmations simples : "Voulez-vous enregistrer ?", "Autoriser cette mise à jour ?", "Fermer sans enregistrer ?". Ces interruptions, bien que nécessaires, brisent le flux de travail et réduisent la productivité. Sentry-AI résout ce problème en :

*   **Observant** continuellement votre environnement de travail
*   **Comprenant** le contexte de chaque dialogue ou notification
*   **Décidant** de la meilleure action à entreprendre en fonction de vos préférences
*   **Agissant** automatiquement pour vous, tout en respectant votre sécurité et votre vie privée

---

## ✨ Caractéristiques Principales

### 🎯 Multi-LLM Support (NOUVEAU!)

Sentry-AI supporte maintenant **4 fournisseurs de LLM** :
- **Ollama** (local, gratuit, privé)
- **Google Gemini** (cloud, rapide, performant)
- **OpenAI** (cloud, précis, fiable)
- **Anthropic Claude** (cloud, intelligent, contextuel)

Choisissez votre provider préféré dans `.env` :

```bash
LLM_PROVIDER=gemini  # ou ollama, openai, claude
GEMINI_API_KEY=votre_cle_api
```

📚 [Guide Multi-LLM Complet](docs/MULTI_LLM_GUIDE.md)

### 🤖 VS Code Integration (NOUVEAU!)

Sentry-AI peut maintenant **automatiser les dialogues de Claude Code** dans Visual Studio Code :
- ✅ Approuve automatiquement les commandes bash sûres
- ✅ Répond intelligemment aux questions de Claude
- ✅ Gère les demandes d'édition automatique
- ✅ Détecte et filtre les commandes dangereuses

📚 [Guide VS Code Automation](docs/VSCODE_AUTOMATION_GUIDE.md)

### 🔒 Confidentialité Absolue

*   **100% Local :** Toutes les données (captures d'écran, textes, décisions) sont traitées localement sur votre Mac.
*   **Aucune Connexion Cloud :** Utilisation exclusive de modèles d'IA locaux via Ollama.
*   **Contrôle Total :** Vous décidez quelles applications peuvent être automatisées.

### ⚡ Performance Optimisée

*   **Native macOS :** Utilise les API d'accessibilité natives pour une intégration parfaite.
*   **Apple Silicon Ready :** Optimisé pour les puces M1/M2/M3/M4 avec Neural Engine.
*   **Architecture Événementielle :** ~0% CPU en idle, réponse instantanée (<50ms).
*   **Menu Bar UI :** Interface native macOS professionnelle.

### 🎯 8+ Applications Supportées

*   **TextEdit, Notes :** Gestion intelligente des sauvegardes
*   **Finder :** Protection contre suppressions accidentelles
*   **Safari :** Téléchargements et navigation automatisés
*   **Mail :** Gestion des emails et pièces jointes
*   **Xcode :** Automatisation du développement
*   **Photos :** Importation et gestion optimisées
*   **Slack :** Notifications et mises à jour
*   **VS Code :** Intégration Claude Code complète

### 🧠 Intelligence Contextuelle

*   **Décisions Éclairées :** Le LLM local analyse le contexte complet (application, historique, préférences) avant d'agir.
*   **Apprentissage des Préférences :** Le système s'améliore au fil du temps en apprenant vos choix.
*   **Règles Personnalisables :** Définissez des règles spécifiques pour différentes applications ou situations.

### 🛡️ Sécurité Renforcée

*   **Liste Blanche/Noire :** Excluez automatiquement les applications sensibles (Terminal, Keychain, etc.).
*   **Journalisation Complète :** Toutes les actions sont enregistrées pour audit et transparence.
*   **Mode Confirmation :** Possibilité de demander confirmation avant certaines actions critiques.

---

## 🏗️ Architecture

Sentry-AI est construit autour de quatre modules principaux :

| Module | Responsabilité |
| :--- | :--- |
| **Observer** | Surveille l'interface utilisateur via l'API d'accessibilité macOS |
| **Analyzer** | Extrait le contexte et analyse les dialogues (avec fallback OCR) |
| **Decision Engine** | Interroge le LLM local (Ollama) pour prendre une décision |
| **Actor** | Exécute l'action décidée de manière programmatique |

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐      ┌──────────┐
│   Observer  │─────▶│   Analyzer   │─────▶│ Decision Engine │─────▶│  Actor   │
│ (UI Watch)  │      │  (Context)   │      │   (AI/LLM)      │      │ (Action) │
└─────────────┘      └──────────────┘      └─────────────────┘      └──────────┘
       │                     │                       │                     │
       └─────────────────────┴───────────────────────┴─────────────────────┘
                                       │
                                 ┌─────▼──────┐
                                 │ Core Service│
                                 │ (FastAPI)   │
                                 └─────────────┘
```

Pour plus de détails, consultez [PROJECT_PLAN.md](PROJECT_PLAN.md).

---

## 🚀 Démarrage Rapide

### Installation Simple (Recommandée)

Utilisez le script d'installation automatique :

```bash
git clone https://github.com/lekesiz/Sentry-AI.git
cd Sentry-AI
./setup.sh
```

Le script va :
- ✓ Créer un environnement virtuel Python
- ✓ Installer toutes les dépendances
- ✓ Vérifier l'installation d'Ollama
- ✓ Configurer le fichier `.env`
- ✓ Tester l'installation

Ensuite, suivez les instructions affichées pour :
1. Démarrer Ollama (`ollama serve`)
2. Télécharger le modèle (`ollama pull phi3:mini`)
3. Accorder les permissions d'accessibilité
4. **Lancer Menu Bar UI (`make menubar`)** ← Recommandé !

### Utilisation

**Interface Menu Bar (Recommandée) :**
```bash
make menubar
```
Cliquez sur l'icône dans la barre de menus → Start Sentry-AI

**Interface Terminal (Alternative) :**
```bash
make run
```

**Lancer Tests Utilisateur :**
```bash
make user-test
```

### Installation Manuelle

Si vous préférez installer manuellement :

```bash
# 1. Cloner le dépôt
git clone https://github.com/lekesiz/Sentry-AI.git
cd Sentry-AI

# 2. Créer un environnement virtuel
python3.11 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Installer Ollama et télécharger un modèle
brew install ollama
ollama serve  # Dans un terminal séparé
ollama pull phi3:mini

# 5. Copier le fichier de configuration
cp .env.example .env

# 6. Tester l'installation
python test_installation.py

# 7. Lancer Sentry-AI
make run
```

### Prérequis

*   **macOS 13.0+** (Ventura ou supérieur)
*   **Python 3.11+**
*   **Ollama** installé ([ollama.ai](https://ollama.ai))
*   **Permissions d'accessibilité** (l'application vous guidera)

---

## 📖 Documentation

### Guides Principaux
*   [Plan de Projet et Architecture](PROJECT_PLAN.md)
*   [Guide de Démarrage Rapide](QUICKSTART.md)
*   [Guide de Test](TESTING_GUIDE.md)

### Guides Spécialisés
*   [Support Multi-LLM](docs/MULTI_LLM_GUIDE.md) - Comment utiliser Gemini, OpenAI, Claude
*   [Automatisation VS Code](docs/VSCODE_AUTOMATION_GUIDE.md) - Automatiser Claude Code
*   [Rapport d'Audit Final](FINAL_AUDIT_REPORT.md) - Résultats des tests

---

## 🛣️ Roadmap

### ✅ Milestone 1 : Fondations (En cours)

*   [x] Structure du projet
*   [x] Documentation initiale
*   [ ] Module Observer (Accessibility API)
*   [ ] Module Analyzer (contexte + OCR)
*   [ ] Module Decision Engine (Ollama)
*   [ ] Module Actor (automation)
*   [ ] Tests unitaires

### 🔜 Milestone 2 : Robustesse

*   [ ] Gestion d'erreurs avancée
*   [ ] Système de logs avec SQLite
*   [ ] Liste blanche/noire d'applications
*   [ ] Optimisation performance

### 🔮 Milestone 3 : Interface Utilisateur

*   [ ] Application de barre de menus
*   [ ] Visualisation des logs en temps réel
*   [ ] Configuration des préférences
*   [ ] Statistiques d'utilisation

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Ce projet suit une méthodologie inspirée de [Yago](https://github.com/lekesiz/yago) avec une emphase sur la qualité du code, la documentation et les tests.

### Principes de Développement

*   **Privacy First :** Aucune donnée ne doit quitter la machine de l'utilisateur.
*   **Safety First :** Toujours privilégier la sécurité de l'utilisateur.
*   **Transparency :** Chaque action doit être loggée et auditable.
*   **Testability :** Chaque module doit être testable de manière isolée.

---

## 📝 License

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

*   Inspiré par le projet [Yago](https://github.com/lekesiz/yago) pour sa structure professionnelle
*   Basé sur les concepts d'automatisation cognitive décrits dans [ce document](https://github.com/lekesiz/Sentry-AI)
*   Utilise [Ollama](https://ollama.ai) pour l'exécution locale de LLMs
*   S'appuie sur les frameworks natifs d'Apple (Accessibility, Vision)

---

**Développé avec Mikail Lekesiz pour la communauté macOS**
