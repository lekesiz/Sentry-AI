# 🚀 Guide de Démarrage Rapide - Sentry-AI

Ce guide vous aidera à démarrer avec Sentry-AI en quelques minutes.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :

*   **macOS 13.0+** (Ventura ou supérieur)
*   **Python 3.11+** installé
*   **Homebrew** (pour installer Ollama)
*   Environ **5 Go d'espace disque** pour les modèles LLM

---

## 📦 Installation

### Étape 1 : Installer Ollama

Ollama est nécessaire pour exécuter les modèles d'IA localement.

```bash
# Installer Ollama via Homebrew
brew install ollama

# Démarrer le service Ollama
ollama serve
```

Dans un nouveau terminal, téléchargez le modèle :

```bash
# Télécharger le modèle Phi-3 (recommandé, ~2.3 Go)
ollama pull phi3:mini

# Ou pour un modèle plus puissant (optionnel)
ollama pull llama3:8b
```

### Étape 2 : Cloner le Projet

```bash
git clone https://github.com/lekesiz/Sentry-AI.git
cd Sentry-AI
```

### Étape 3 : Créer un Environnement Virtuel

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Étape 4 : Installer les Dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Permissions d'Accessibilité

Sentry-AI a besoin d'accéder à l'API d'accessibilité de macOS. Au premier lancement, macOS vous demandera d'autoriser l'application.

1.  Ouvrez **Réglages Système** > **Confidentialité et sécurité** > **Accessibilité**
2.  Ajoutez **Terminal** (ou votre terminal préféré) à la liste
3.  Cochez la case pour activer l'accès

### Configuration Optionnelle

Créez un fichier `.env` à la racine du projet pour personnaliser les paramètres :

```bash
# .env
OLLAMA_MODEL=phi3:mini
OBSERVER_INTERVAL=2.0
LOG_LEVEL=INFO
```

---

## 🎯 Premier Lancement

### Mode Test (Recommandé pour débuter)

Lancez Sentry-AI en mode test pour voir comment il fonctionne :

```bash
python -m sentry_ai.main
```

Vous devriez voir :

```
2025-10-31 10:00:00 | INFO     | Initializing Sentry-AI v1.0.0
2025-10-31 10:00:00 | INFO     | All agents initialized successfully
2025-10-31 10:00:00 | INFO     | Starting Sentry-AI...
2025-10-31 10:00:00 | INFO     | Observer started
```

### Tester avec TextEdit

1.  Ouvrez **TextEdit**
2.  Tapez du texte
3.  Essayez de fermer la fenêtre sans enregistrer
4.  Sentry-AI devrait détecter la boîte de dialogue et proposer une action

---

## 🧪 Exécuter les Tests

Pour vérifier que tout fonctionne correctement :

```bash
# Exécuter tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ --cov=sentry_ai --cov-report=html
```

---

## 🛑 Arrêter Sentry-AI

Pour arrêter l'application, appuyez sur **Ctrl+C** dans le terminal.

---

## 📚 Prochaines Étapes

*   Consultez [PROJECT_PLAN.md](PROJECT_PLAN.md) pour comprendre l'architecture
*   Lisez [README.md](README.md) pour les fonctionnalités complètes
*   Personnalisez la liste blanche/noire d'applications dans `sentry_ai/core/config.py`

---

## 🆘 Dépannage

### Problème : "Ollama not available"

**Solution :** Vérifiez qu'Ollama est en cours d'exécution :

```bash
ollama list  # Devrait afficher les modèles installés
```

### Problème : "macOS frameworks not available"

**Solution :** Assurez-vous que `pyobjc` est correctement installé :

```bash
pip install --force-reinstall pyobjc-core pyobjc-framework-Cocoa
```

### Problème : Aucun dialogue détecté

**Solution :** Vérifiez que :
1.  Les permissions d'accessibilité sont accordées
2.  L'application n'est pas dans la liste noire
3.  Le dialogue contient au moins 2 boutons

---

## 💡 Conseils

*   **Commencez avec des applications simples** comme TextEdit ou Notes
*   **Activez le mode debug** en modifiant `LOG_LEVEL=DEBUG` dans `.env`
*   **Consultez les logs** dans `sentry_ai.log` pour diagnostiquer les problèmes

---

**Bon automatisation ! 🤖**
