# Gemini API Setup Guide for Sentry-AI

## Quick Start

Follow these steps to use Google Gemini with Sentry-AI:

---

## Step 1: Get Your Gemini API Key

1. Go to **Google AI Studio**: https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy the API key (starts with `AIza...`)

---

## Step 2: Configure Sentry-AI

Open your `.env` file and update these lines:

```bash
# LLM Provider Configuration
LLM_PROVIDER=gemini

# Gemini API Key
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

**Important:** Replace `YOUR_API_KEY_HERE` with your actual Gemini API key.

---

## Step 3: Enable Fallback (Optional but Recommended)

Add fallback support in case Gemini fails:

```bash
# LLM Fallback Configuration
LLM_FALLBACK_ENABLED=True
LLM_FALLBACK_ORDER=["gemini","ollama"]
```

This will use Gemini first, then fall back to Ollama (local) if Gemini fails.

---

## Step 4: Test the Configuration

Run this command to test:

```bash
cd ~/Sentry-AI
source venv/bin/activate
python -c "
from sentry_ai.core.config import settings
from sentry_ai.core.llm_fallback import fallback_manager

print(f'LLM Provider: {settings.llm_provider}')
print(f'Gemini API Key: {settings.gemini_api_key[:10]}...' if settings.gemini_api_key else 'Not set')
print(f'Available providers: {fallback_manager.get_available_providers()}')
"
```

**Expected output:**
```
LLM Provider: gemini
Gemini API Key: AIzaSyBTTq...
Available providers: ['gemini']
```

---

## Step 5: Run Sentry-AI

```bash
make run
```

Sentry-AI will now use Gemini for all AI decisions!

---

## Complete .env Example

Here's a complete `.env` file configured for Gemini:

```bash
# Application Settings
DEBUG=False
LOG_LEVEL=INFO
LOG_FILE=sentry_ai.log
LOG_RETENTION_DAYS=30

# LLM Provider Configuration
LLM_PROVIDER=gemini
LLM_MODEL=  # leave empty for default (gemini-2.0-flash-exp)
LLM_TEMPERATURE=0.1

# Gemini API Key
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

# LLM Fallback Configuration
LLM_FALLBACK_ENABLED=True
LLM_FALLBACK_ORDER=["gemini","ollama"]

# Observer Settings
OBSERVER_INTERVAL=2.0
OBSERVER_ENABLED=True

# Database Settings
DATABASE_URL=sqlite:///./sentry_ai.db

# API Settings
API_HOST=127.0.0.1
API_PORT=8000

# Security Settings
BLACKLIST_APPS=[]
REQUIRE_CONFIRMATION_FOR=[]
```

---

## Troubleshooting

### Problem: "Gemini provider not available"

**Solution:**
1. Check your API key is correct in `.env`
2. Ensure you have `google-genai` installed:
   ```bash
   pip install google-genai==1.47.0
   ```
3. Test the API key manually:
   ```bash
   python -c "
   from google import genai
   client = genai.Client(api_key='YOUR_API_KEY')
   print('✓ API key works!')
   "
   ```

### Problem: "API key validation error"

**Solution:**
Make sure your API key in `.env` has **NO quotes** around it:

**Wrong:**
```bash
GEMINI_API_KEY="AIzaSyBTTqfH2..."
```

**Correct:**
```bash
GEMINI_API_KEY=AIzaSyBTTqfH2...
```

### Problem: "Rate limit exceeded"

**Solution:**
Gemini has rate limits. If you hit them:
1. Wait a few minutes
2. Or enable fallback to use Ollama as backup:
   ```bash
   LLM_FALLBACK_ENABLED=True
   LLM_FALLBACK_ORDER=["gemini","ollama"]
   ```

---

## Why Use Gemini?

| Feature | Gemini | Ollama (Local) |
|---------|--------|----------------|
| **Speed** | ⚡ Very fast | 🐢 Slower |
| **Quality** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Good |
| **Cost** | 💰 Free tier available | 💰 Free |
| **Privacy** | ☁️ Cloud (Google) | 🔒 100% local |
| **Setup** | ✅ Easy (just API key) | ⚙️ Requires installation |

**Recommended:** Use Gemini as primary with Ollama as backup!

---

## Next Steps

1. ✅ Get Gemini API key
2. ✅ Update `.env` file
3. ✅ Test configuration
4. ✅ Run Sentry-AI
5. 🎉 Enjoy AI-powered automation!

For more details, see:
- **LLM_FALLBACK_GUIDE.md** - Full fallback system documentation
- **MULTI_LLM_GUIDE.md** - Compare all LLM providers

---

**Happy automating! 🚀**
