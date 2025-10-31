# 🤖 Guide Multi-LLM - Sentry-AI

Ce guide explique comment utiliser différents fournisseurs de LLM (Large Language Models) avec Sentry-AI.

---

## 🎯 Fournisseurs Supportés

Sentry-AI supporte maintenant **4 fournisseurs de LLM** :

| Fournisseur | Type | Modèle par Défaut | Avantages |
|-------------|------|-------------------|-----------|
| **Ollama** | Local | `phi3:mini` | 🔒 100% privé, gratuit, offline |
| **Google Gemini** | Cloud | `gemini-2.0-flash-exp` | ⚡ Rapide, performant, multimodal |
| **OpenAI** | Cloud | `gpt-4o-mini` | 🎯 Précis, fiable, bien documenté |
| **Anthropic Claude** | Cloud | `claude-3-5-sonnet-20241022` | 🧠 Intelligent, contextuel, sûr |

---

## ⚙️ Configuration

### 1. Choisir un Fournisseur

Éditez votre fichier `.env` :

```bash
# Choisissez un fournisseur
LLM_PROVIDER=ollama  # ou gemini, openai, claude

# Optionnel: spécifiez un modèle personnalisé
LLM_MODEL=  # Laissez vide pour utiliser le modèle par défaut

# Température (0.0 = déterministe, 1.0 = créatif)
LLM_TEMPERATURE=0.1
```

### 2. Configuration Spécifique par Fournisseur

#### Option A: Ollama (Local)

**Avantages :** Gratuit, privé, offline  
**Inconvénients :** Nécessite installation locale, moins performant

```bash
# Installation
brew install ollama
ollama serve  # Dans un terminal séparé
ollama pull phi3:mini

# Configuration .env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3:mini
```

#### Option B: Google Gemini

**Avantages :** Rapide, performant, gratuit (quota généreux)  
**Inconvénients :** Nécessite connexion internet, données envoyées à Google

```bash
# 1. Obtenez une clé API
# Visitez: https://aistudio.google.com/apikey

# 2. Configuration .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=votre_cle_api_ici
LLM_MODEL=gemini-2.0-flash-exp  # Optionnel
```

**Modèles disponibles :**
- `gemini-2.0-flash-exp` (recommandé - rapide et performant)
- `gemini-1.5-pro` (plus puissant mais plus lent)
- `gemini-1.5-flash` (équilibré)

#### Option C: OpenAI

**Avantages :** Très performant, bien documenté  
**Inconvénients :** Payant, nécessite connexion internet

```bash
# 1. Obtenez une clé API
# Visitez: https://platform.openai.com/api-keys

# 2. Configuration .env
LLM_PROVIDER=openai
OPENAI_API_KEY=votre_cle_api_ici
LLM_MODEL=gpt-4o-mini  # Optionnel
```

**Modèles disponibles :**
- `gpt-4o-mini` (recommandé - rapide et économique)
- `gpt-4o` (plus puissant)
- `gpt-4-turbo` (équilibré)

#### Option D: Anthropic Claude

**Avantages :** Très intelligent, excellent pour le contexte  
**Inconvénients :** Payant, nécessite connexion internet

```bash
# 1. Obtenez une clé API
# Visitez: https://console.anthropic.com/settings/keys

# 2. Configuration .env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=votre_cle_api_ici
LLM_MODEL=claude-3-5-sonnet-20241022  # Optionnel
```

**Modèles disponibles :**
- `claude-3-5-sonnet-20241022` (recommandé - équilibré)
- `claude-3-opus-20240229` (plus puissant)
- `claude-3-haiku-20240307` (plus rapide)

---

## 🧪 Tester Votre Configuration

Utilisez le script de test intégré :

```bash
python -c "
from sentry_ai.core.llm_provider import LLMProviderFactory
from sentry_ai.core.config import settings

# Afficher le fournisseur configuré
print(f'Provider: {settings.llm_provider}')

# Tester la disponibilité
available = LLMProviderFactory.get_available_providers()
print(f'Available providers: {[p.value for p in available]}')
"
```

---

## 💡 Recommandations

### Pour le Développement

**Utilisez Ollama** :
- ✅ Gratuit
- ✅ Pas besoin de clé API
- ✅ Fonctionne offline
- ✅ Données privées

### Pour la Production

**Utilisez Gemini ou OpenAI** :
- ✅ Plus performant
- ✅ Plus rapide
- ✅ Meilleure compréhension du contexte
- ⚠️ Nécessite clé API
- ⚠️ Coûts à prévoir

### Pour la Confidentialité Maximale

**Utilisez Ollama uniquement** :
- ✅ 100% local
- ✅ Aucune donnée envoyée à l'extérieur
- ✅ Conforme RGPD

---

## 🔄 Changer de Fournisseur

Vous pouvez changer de fournisseur à tout moment :

1. Éditez `.env`
2. Changez `LLM_PROVIDER`
3. Ajoutez la clé API si nécessaire
4. Redémarrez Sentry-AI

```bash
# Exemple: passer d'Ollama à Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=votre_cle_ici
```

---

## 📊 Comparaison des Performances

| Critère | Ollama | Gemini | OpenAI | Claude |
|---------|--------|--------|--------|--------|
| **Vitesse** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Précision** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Coût** | Gratuit | Gratuit* | Payant | Payant |
| **Confidentialité** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Offline** | ✅ | ❌ | ❌ | ❌ |

*Gemini offre un quota gratuit généreux

---

## 🆘 Dépannage

### "Provider not available"

**Solution :** Vérifiez que :
1. La clé API est correcte (pour cloud providers)
2. Ollama est démarré (pour Ollama)
3. Les dépendances sont installées (`pip install -r requirements.txt`)

### "API key not found"

**Solution :** Ajoutez la clé API dans `.env` :
```bash
GEMINI_API_KEY=votre_cle
OPENAI_API_KEY=votre_cle
ANTHROPIC_API_KEY=votre_cle
```

### "Model not found"

**Solution :** Vérifiez le nom du modèle dans la documentation du fournisseur.

---

## 📝 Notes Importantes

1. **Sécurité :** Ne commitez JAMAIS vos clés API dans Git
2. **Coûts :** Surveillez votre utilisation pour les providers payants
3. **Confidentialité :** Utilisez Ollama si vous traitez des données sensibles
4. **Performance :** Les providers cloud sont généralement plus rapides

---

**Développé avec ❤️ pour la communauté macOS**
