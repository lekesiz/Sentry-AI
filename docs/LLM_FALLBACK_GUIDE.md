# LLM Fallback System Guide

## Overview

Sentry-AI now includes an **automatic fallback system** that tries multiple LLM providers in sequence until one succeeds. This ensures maximum reliability and uptime.

---

## How It Works

When Sentry-AI needs to make a decision, it:

1. **Tries the first provider** in the fallback order
2. **If it fails**, automatically tries the next provider
3. **Continues** until a provider succeeds or all fail
4. **Falls back to rule-based logic** if all AI providers fail

---

## Configuration

### 1. Enable/Disable Fallback

In `.env`:

```bash
LLM_FALLBACK_ENABLED=True  # or False to disable
```

### 2. Set Fallback Order

Define the order of providers to try (JSON array format):

```bash
LLM_FALLBACK_ORDER=["claude","openai","gemini","ollama"]
```

**Default order:** Claude → OpenAI → Gemini → Ollama

### 3. Configure API Keys

Add API keys for the providers you want to use:

```bash
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_claude_key_here
```

**Note:** Ollama doesn't require an API key (runs locally).

---

## Example Scenarios

### Scenario 1: Primary Provider Fails

**Setup:**
```bash
LLM_FALLBACK_ORDER=["gemini","openai","ollama"]
GEMINI_API_KEY=invalid_key
OPENAI_API_KEY=valid_key
```

**What happens:**
1. Tries Gemini → **Fails** (invalid key)
2. Tries OpenAI → **Succeeds** ✓
3. Decision is made using OpenAI

### Scenario 2: All Cloud Providers Fail

**Setup:**
```bash
LLM_FALLBACK_ORDER=["claude","openai","gemini","ollama"]
# All API keys invalid or missing
```

**What happens:**
1. Tries Claude → **Fails**
2. Tries OpenAI → **Fails**
3. Tries Gemini → **Fails**
4. Tries Ollama → **Succeeds** ✓ (local, no API key needed)

### Scenario 3: All Providers Fail

**Setup:**
```bash
LLM_FALLBACK_ORDER=["gemini"]
GEMINI_API_KEY=invalid_key
# Ollama not running
```

**What happens:**
1. Tries Gemini → **Fails**
2. No more providers → **Falls back to rule-based logic**
3. Decision is made using simple rules (Save > Don't Save, etc.)

---

## Recommended Configurations

### For Maximum Reliability

Use all providers with valid API keys:

```bash
LLM_FALLBACK_ENABLED=True
LLM_FALLBACK_ORDER=["claude","openai","gemini","ollama"]
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

**Pros:**
- ✅ Highest uptime
- ✅ Always has a backup
- ✅ Works even if 3 providers fail

**Cons:**
- ❌ Requires 3 paid API keys
- ❌ Higher cost

### For Cost Efficiency

Use one paid provider + Ollama as backup:

```bash
LLM_FALLBACK_ENABLED=True
LLM_FALLBACK_ORDER=["gemini","ollama"]
GEMINI_API_KEY=your_key
```

**Pros:**
- ✅ Lower cost (only 1 paid API)
- ✅ Still has local backup
- ✅ Good balance

**Cons:**
- ❌ If Gemini fails and Ollama is down, falls back to rules

### For Privacy (Local Only)

Use only Ollama:

```bash
LLM_FALLBACK_ENABLED=False
LLM_PROVIDER=ollama
```

**Pros:**
- ✅ 100% private (no data leaves your Mac)
- ✅ Free
- ✅ No API keys needed

**Cons:**
- ❌ Requires Ollama to be running
- ❌ No backup if Ollama fails

---

## Monitoring

Sentry-AI logs which provider is being used:

```
INFO: Trying claude provider...
WARNING: claude failed: Invalid API key
INFO: Trying openai provider...
SUCCESS: ✓ openai succeeded
```

Check `sentry_ai.log` to see which providers are working.

---

## Troubleshooting

### Problem: "All LLM providers failed"

**Solution:**
1. Check your API keys in `.env`
2. Verify Ollama is running (`ollama list`)
3. Test each provider individually

### Problem: "No LLM providers available"

**Solution:**
1. Check `LLM_FALLBACK_ENABLED=True` in `.env`
2. Ensure at least one provider has a valid API key
3. Or install and run Ollama

### Problem: Fallback is too slow

**Solution:**
1. Reduce the number of providers in `LLM_FALLBACK_ORDER`
2. Put the fastest provider first
3. Remove providers with invalid keys

---

## Best Practices

1. **Test your API keys** before relying on them
2. **Monitor logs** to see which providers are being used
3. **Keep Ollama running** as a free backup
4. **Update API keys** before they expire
5. **Use the fastest provider first** in the fallback order

---

## API Key Links

- **Gemini:** https://aistudio.google.com/apikey
- **OpenAI:** https://platform.openai.com/api-keys
- **Claude:** https://console.anthropic.com/settings/keys
- **Ollama:** No API key needed (local)

---

## Summary

The fallback system makes Sentry-AI **more reliable** by automatically trying multiple providers. Configure it once and forget about it!

**Recommended setup for most users:**

```bash
LLM_FALLBACK_ENABLED=True
LLM_FALLBACK_ORDER=["gemini","ollama"]
GEMINI_API_KEY=your_key_here
```

This gives you a fast cloud provider with a free local backup! 🚀
