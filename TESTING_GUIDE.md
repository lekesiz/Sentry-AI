# 🧪 Guide de Test Complet - Sentry-AI

Ce guide vous explique comment tester Sentry-AI sur votre Mac pour vous assurer que tout fonctionne correctement.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir suivi le **[QUICKSTART.md](QUICKSTART.md)** et que :

1.  **Ollama est installé et en cours d'exécution**.
2.  Le modèle `phi3:mini` est téléchargé (`ollama pull phi3:mini`).
3.  Les dépendances Python sont installées (`pip install -r requirements.txt`).
4.  Les **permissions d'accessibilité** sont accordées pour votre terminal.

---

## 1️⃣ Étape 1 : Vérification de l'Installation

J'ai créé un script simple pour vérifier que toutes les dépendances sont correctement installées.

**Action :**

À la racine du projet, exécutez :

```bash
python test_installation.py
```

**Résultat Attendu :**

Vous devriez voir un message de succès :

```
✅ SUCCESS: All critical dependencies are installed!

⚠️  X warning(s):
   - ... (des avertissements pour les modules macOS sont normaux si vous n'êtes pas sur Mac)

Sentry-AI is ready to use!
Run: python -m sentry_ai.main
```

Si vous voyez des erreurs critiques, cela signifie qu'une dépendance est manquante. Essayez de réinstaller les dépendances avec `pip install -r requirements.txt`.

---

## 2️⃣ Étape 2 : Test des Unités et de l'Intégration

Nous allons maintenant exécuter la suite de tests automatisés pour vérifier la logique interne du programme.

**Action :**

Utilisez le `Makefile` pour lancer les tests :

```bash
make test
```

**Résultat Attendu :**

Tous les tests devraient passer avec succès. Vous verrez une sortie similaire à :

```
============================= test session starts ==============================
...
collected XX items

tests/test_agents.py::TestAnalyzer::test_analyze_save_dialog PASSED
tests/test_agents.py::TestAnalyzer::test_analyze_no_buttons PASSED
...
tests/test_integration.py::TestAPIIntegration::test_api_get_config PASSED

============================== XX passed in X.XXs ==============================
```

---

## 3️⃣ Étape 3 : Test End-to-End (Cas d'Usage Réel)

C'est le test le plus important. Nous allons lancer Sentry-AI et voir comment il réagit à un vrai dialogue système.

### A. Lancer Sentry-AI

**Action :**

Dans votre terminal, lancez l'application principale :

```bash
make run
```

**Résultat Attendu :**

Sentry-AI va démarrer et commencer à surveiller votre système. Vous devriez voir :

```
INFO:     Initializing Sentry-AI v1.0.0
INFO:     All agents initialized successfully
INFO:     Starting Sentry-AI...
INFO:     Observer started
```

L'agent est maintenant actif et attend qu'un dialogue apparaisse.

### B. Déclencher un Dialogue

**Action :**

1.  Ouvrez l'application **TextEdit**.
2.  Tapez quelques mots dans le document.
3.  Essayez de fermer la fenêtre en cliquant sur le bouton rouge en haut à gauche.

**Résultat Attendu :**

Un dialogue "Voulez-vous enregistrer les modifications ?" va apparaître. Presque immédiatement, vous devriez voir Sentry-AI réagir dans votre terminal :

```
INFO:     Processing dialog from TextEdit
INFO:     Analyzed dialog: save_confirmation with options: ["Enregistrer", "Supprimer", "Annuler"]
INFO:     AI decision: 'Enregistrer' (confirmation required: False)
SUCCESS:  Successfully automated TextEdit: clicked 'Enregistrer' (123.4ms)
```

Le dialogue "Enregistrer" de TextEdit devrait alors s'ouvrir automatiquement, prouvant que Sentry-AI a bien cliqué sur le bouton.

---

## 4️⃣ Étape 4 : Test de l'API (Optionnel)

Si vous souhaitez interagir avec Sentry-AI via son API.

### A. Lancer le Serveur API

**Action :**

Ouvrez un **deuxième terminal** et lancez le serveur API :

```bash
make api
```

### B. Interagir avec l'API

**Action :**

Ouvrez votre navigateur et allez à l'une de ces adresses :

-   **Statut :** `http://127.0.0.1:8000/status`
-   **Logs :** `http://127.0.0.1:8000/logs`
-   **Statistiques :** `http://127.0.0.1:8000/statistics`
-   **Documentation API :** `http://127.0.0.1:8000/docs`

**Résultat Attendu :**

Vous devriez voir des données JSON dans votre navigateur, confirmant que l'API fonctionne et communique avec la base de données.

---

## 🆘 En Cas de Problème

-   **"ModuleNotFoundError"** : Assurez-vous d'avoir activé votre environnement virtuel (`source venv/bin/activate`) et d'avoir lancé `pip install -r requirements.txt`.

-   **Aucune détection de dialogue** : Vérifiez que les **permissions d'accessibilité** sont bien accordées à votre terminal dans les `Réglages Système` > `Confidentialité et sécurité` > `Accessibilité`.

-   **Erreur Ollama** : Assurez-vous que l'application Ollama est lancée et que le modèle `phi3:mini` est bien téléchargé (`ollama list` pour vérifier).

---

Si vous suivez ces étapes, vous devriez être en mesure de tester complètement le projet. N'hésitez pas si vous rencontrez le moindre problème !
