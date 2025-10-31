# 🤖 Guide d'Automatisation VS Code - Sentry-AI

Ce guide explique comment utiliser Sentry-AI pour automatiser les dialogues de Claude Code dans Visual Studio Code.

---

## 🎯 Cas d'Usage

Vous développez avec **Visual Studio Code** et l'extension **Claude Code**. Claude vous aide à coder, mais vous pose constamment des questions :

- ✅ "Allow this bash command?" → **Vous devez cliquer "Yes"**
- ✅ "Edit automatically?" → **Vous devez cliquer "Yes"**
- ❓ "Quelle est la structure de votre base de données?" → **Vous devez taper une réponse**

**Problème :** Vous devez rester devant votre ordinateur pendant des heures pour cliquer et répondre.

**Solution :** Sentry-AI automatise tout cela ! 🚀

---

## ⚙️ Configuration

### 1. Activer l'Automatisation VS Code

Éditez votre fichier `.env` :

```bash
# Activer l'Observer VS Code
OBSERVER_ENABLED=True
OBSERVER_INTERVAL=1.0  # Vérifier toutes les secondes

# Choisir un LLM pour les réponses intelligentes
LLM_PROVIDER=gemini  # ou ollama, openai, claude
GEMINI_API_KEY=votre_cle_api
```

### 2. Configurer les Stratégies

Sentry-AI utilise des **stratégies** pour décider comment répondre aux dialogues.

#### Stratégie A : Commandes Bash

**Par défaut :** Approuve automatiquement les commandes sûres, rejette les dangereuses.

**Commandes sûres :**
- `ls`, `pwd`, `cat`, `grep`, `find`
- `python`, `node`, `npm`, `pip`
- `git status`, `git log`, `git diff`

**Commandes dangereuses :**
- `rm -rf`, `sudo`, `chmod`, `dd`
- Redirections (`>`, `>>`)
- `kill`, `pkill`

**Personnalisation :**

```python
# Dans votre code
from sentry_ai.agents.vscode_strategies import ClaudeBashCommandStrategy

strategy = ClaudeBashCommandStrategy(
    auto_approve=True,  # Approuver automatiquement
    safe_commands_only=True  # Seulement les commandes sûres
)
```

#### Stratégie B : Édition Automatique

**Par défaut :** Approuve automatiquement les demandes d'édition.

**Personnalisation :**

```python
from sentry_ai.agents.vscode_strategies import ClaudeEditAutomaticallyStrategy

strategy = ClaudeEditAutomaticallyStrategy(
    auto_approve=True  # Approuver automatiquement
)
```

#### Stratégie C : Questions de Claude

**Par défaut :** Utilise un LLM pour générer des réponses intelligentes.

**Exemple :**
- Claude demande : "Quelle est la structure de votre base de données?"
- Sentry-AI génère : "Nous utilisons PostgreSQL avec Prisma. La structure principale inclut des tables users, projects, et tasks."

---

## 🚀 Utilisation

### Mode 1 : Automatisation Complète

Lancez Sentry-AI et laissez-le gérer tout automatiquement :

```bash
python sentry_ai/main.py
```

Sentry-AI va :
1. ✅ Détecter les dialogues Claude dans VS Code
2. ✅ Analyser le contexte
3. ✅ Prendre une décision intelligente
4. ✅ Cliquer ou taper la réponse
5. ✅ Continuer à surveiller

### Mode 2 : Avec Confirmation

Pour plus de sécurité, activez le mode confirmation :

```bash
# Dans .env
REQUIRE_CONFIRMATION_FOR=Visual Studio Code
```

Sentry-AI vous demandera confirmation avant d'agir.

### Mode 3 : Observer Seulement

Pour tester sans agir :

```python
from sentry_ai.agents.vscode_observer import VSCodeObserver

observer = VSCodeObserver()

def on_dialog(dialog):
    print(f"Dialog détecté: {dialog.question}")
    print(f"Options: {dialog.options}")

observer.watch(callback=on_dialog, interval=1.0)
```

---

## 📊 Exemples Concrets

### Exemple 1 : Commande Bash Sûre

**Dialog Claude :**
```
Allow this bash command?

$ cat package.json
```

**Décision Sentry-AI :**
- ✅ Commande sûre détectée (`cat`)
- ✅ Clique automatiquement sur "Yes"
- ✅ Reasoning: "Safe command approved: cat package.json"

### Exemple 2 : Commande Bash Dangereuse

**Dialog Claude :**
```
Allow this bash command?

$ rm -rf node_modules
```

**Décision Sentry-AI :**
- ❌ Commande dangereuse détectée (`rm -rf`)
- ❌ Clique automatiquement sur "No"
- ❌ Reasoning: "Dangerous command detected: rm -rf node_modules"

### Exemple 3 : Question de Claude

**Dialog Claude :**
```
What database are you using for this project?
```

**Décision Sentry-AI :**
- 🤖 Utilise Gemini/OpenAI/Claude pour générer une réponse
- ⌨️ Tape la réponse dans le champ de texte
- ✅ Appuie sur Enter
- 💡 Reasoning: "LLM-generated answer to Claude's question"

---

## 🔧 Personnalisation Avancée

### Ajouter une Stratégie Personnalisée

```python
from sentry_ai.agents.vscode_strategies import VSCodeStrategy, VSCodeStrategyManager
from sentry_ai.models.data_models import DialogContext, AIDecision

class MyCustomStrategy(VSCodeStrategy):
    """Ma stratégie personnalisée."""
    
    def can_handle(self, context: DialogContext) -> bool:
        """Vérifier si je peux gérer ce dialogue."""
        return "mon_mot_cle" in context.question.lower()
    
    def decide(self, context: DialogContext) -> AIDecision:
        """Prendre une décision."""
        return AIDecision(
            chosen_option="Yes",
            reasoning="Ma logique personnalisée",
            confidence=0.9
        )

# Ajouter la stratégie
manager = VSCodeStrategyManager()
manager.add_strategy(MyCustomStrategy())
```

### Désactiver une Stratégie

```python
from sentry_ai.agents.vscode_strategies import (
    VSCodeStrategyManager,
    ClaudeBashCommandStrategy
)

manager = VSCodeStrategyManager()
manager.remove_strategy(ClaudeBashCommandStrategy)
```

---

## 📈 Statistiques et Logs

Sentry-AI enregistre toutes les actions dans la base de données :

```bash
# Voir les statistiques
sqlite3 sentry_ai.db "SELECT * FROM actions ORDER BY timestamp DESC LIMIT 10;"
```

**Informations enregistrées :**
- Timestamp
- Application (VS Code)
- Type de dialogue
- Décision prise
- Succès/Échec
- Temps d'exécution

---

## 🆘 Dépannage

### "VS Code dialog not detected"

**Causes possibles :**
1. VS Code n'est pas en cours d'exécution
2. Les permissions d'accessibilité ne sont pas accordées
3. L'Observer est désactivé

**Solutions :**
```bash
# Vérifier que VS Code est en cours d'exécution
ps aux | grep "Visual Studio Code"

# Vérifier les permissions
# Aller dans Réglages Système > Confidentialité > Accessibilité

# Vérifier la configuration
grep OBSERVER_ENABLED .env
```

### "Strategy not found"

**Cause :** Aucune stratégie ne correspond au dialogue.

**Solution :** Ajouter une stratégie personnalisée ou vérifier les logs :

```bash
tail -f sentry_ai.log | grep "No strategy found"
```

### "LLM not available for answering questions"

**Cause :** Aucun LLM configuré pour générer des réponses.

**Solution :**
```bash
# Configurer un LLM dans .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=votre_cle
```

---

## 🎯 Bonnes Pratiques

### 1. Commencez en Mode Observer

Testez d'abord sans automatisation :

```python
observer = VSCodeObserver()
observer.watch(callback=lambda d: print(d.question), interval=1.0)
```

### 2. Activez les Logs Détaillés

```bash
# Dans .env
LOG_LEVEL=DEBUG
```

### 3. Utilisez un LLM Performant

Pour les réponses aux questions, utilisez un LLM puissant :

```bash
LLM_PROVIDER=claude  # ou openai
```

### 4. Surveillez les Statistiques

```bash
# Vérifier le taux de succès
sqlite3 sentry_ai.db "SELECT success, COUNT(*) FROM actions GROUP BY success;"
```

---

## 📝 Scénario Complet

**Situation :** Vous développez une application avec Claude Code pendant 3 heures.

**Sans Sentry-AI :**
- ❌ Vous devez cliquer "Yes" 50+ fois
- ❌ Vous devez répondre à 10+ questions
- ❌ Vous devez rester devant l'ordinateur

**Avec Sentry-AI :**
- ✅ Sentry-AI clique automatiquement sur "Yes" pour les commandes sûres
- ✅ Sentry-AI génère des réponses intelligentes aux questions
- ✅ Vous pouvez faire autre chose pendant que Claude travaille

**Résultat :**
- ⏱️ Gain de temps : **2-3 heures**
- 😌 Moins de stress
- 🚀 Développement plus rapide

---

## 🔐 Sécurité

### Commandes Sûres vs Dangereuses

Sentry-AI utilise une liste blanche/noire pour les commandes :

**Liste Blanche (Sûres) :**
- Lecture seule : `cat`, `ls`, `grep`, `find`
- Outils de développement : `python`, `node`, `npm`, `git`

**Liste Noire (Dangereuses) :**
- Suppression : `rm -rf`
- Privilèges : `sudo`, `chmod`
- Système : `dd`, `mkfs`, `format`

### Recommandations

1. **Toujours activer `safe_commands_only=True`**
2. **Vérifier les logs régulièrement**
3. **Utiliser le mode confirmation pour les tâches critiques**

---

**Développé avec ❤️ pour les développeurs macOS qui utilisent Claude Code**
