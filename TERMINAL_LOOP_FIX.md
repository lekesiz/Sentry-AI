# Terminal Loop Fix Guide

## Problem

Sentry-AI was detecting Terminal dialogs in an infinite loop, even though Terminal was supposed to be blacklisted.

## Root Cause

**Pydantic was not parsing JSON arrays from `.env` correctly.**

When you had `BLACKLIST_APPS=["Terminal"]` in your `.env`, Pydantic was treating it as a string, not a list:

```python
# What we got:
settings.blacklist_apps = ['["Terminal"]']  # Wrong!

# What we needed:
settings.blacklist_apps = ['Terminal']  # Correct!
```

So when checking `if "Terminal" in settings.blacklist_apps`, it would fail because `"Terminal"` is not equal to `'["Terminal"]'`.

## Solution

Added a `field_validator` to the `Settings` class that:
1. Detects JSON strings in `.env`
2. Parses them correctly into Python lists
3. Falls back to comma-separated values if JSON parsing fails

## What Changed

### File: `sentry_ai/core/config.py`

Added this validator:

```python
@field_validator('blacklist_apps', 'whitelist_apps', 'require_confirmation_for', 'llm_fallback_order', mode='before')
@classmethod
def parse_json_list(cls, v):
    """Parse JSON array strings from .env file."""
    if isinstance(v, str):
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
            return [parsed]
        except (json.JSONDecodeError, ValueError):
            # Fallback to comma-separated values
            return [x.strip() for x in v.split(',') if x.strip()]
    return v
```

## How to Apply the Fix

### Step 1: Pull the Latest Code

```bash
cd ~/Sentry-AI
git pull
```

### Step 2: Test the Fix

```bash
# Activate virtual environment
source venv/bin/activate

# Run the test script
python test_blacklist_parsing.py
```

**Expected output:**
```
Testing Blacklist Parsing
============================================================
1. Blacklist Apps: ['Terminal']
   Type: <class 'list'>
   First element: 'Terminal'
   First element type: <class 'str'>

3. Testing is_app_allowed():
   Terminal: ❌ BLOCKED
   TextEdit: ✅ ALLOWED
   Safari: ✅ ALLOWED

✅ SUCCESS: Terminal is correctly blacklisted!
```

### Step 3: Restart Sentry-AI

```bash
# Stop the current instance (Ctrl+C)
# Then restart:
make run
```

## Verification

After restarting, Sentry-AI should:
- ✅ **Ignore Terminal completely** (no more "Dialog detected in Terminal" messages)
- ✅ **Only monitor allowed apps** like TextEdit, Safari, etc.
- ✅ **Respect your fallback order**: Gemini → Ollama

## Your .env Configuration

Your current `.env` is correct:

```bash
BLACKLIST_APPS=["Terminal"]
LLM_FALLBACK_ORDER=["gemini","ollama"]
```

Both formats now work:
- JSON format: `["Terminal","iTerm"]`
- CSV format: `Terminal,iTerm`

## Testing with TextEdit

Once Sentry-AI is running without the Terminal loop:

1. Open **TextEdit**
2. Type something: "Hello Sentry-AI!"
3. Press **Cmd+W** to close
4. **Sentry-AI should automatically click "Save"**

## Logs to Watch

```bash
# In another terminal:
tail -f logs/sentry_ai.log
```

You should see:
```
[INFO] Observer started
[INFO] Blacklisted apps: ['Terminal']
[INFO] Dialog detected in TextEdit
[INFO] Using LLM provider: gemini
[INFO] Decision: Click 'Save' button
[INFO] Action executed successfully
```

**NOT:**
```
[INFO] Dialog detected in Terminal  # ❌ This should NOT appear anymore!
```

## Troubleshooting

### If Terminal is still being detected:

1. **Verify the fix was applied:**
   ```bash
   cd ~/Sentry-AI
   git log -1 --oneline
   # Should show: "fix: Add JSON parser for list fields in .env"
   ```

2. **Check your .env:**
   ```bash
   grep BLACKLIST_APPS .env
   # Should output: BLACKLIST_APPS=["Terminal"]
   ```

3. **Run the test again:**
   ```bash
   source venv/bin/activate
   python test_blacklist_parsing.py
   ```

4. **Check logs:**
   ```bash
   grep "Blacklisted apps" logs/sentry_ai.log
   # Should show: Blacklisted apps: ['Terminal']
   # NOT: Blacklisted apps: ['["Terminal"]']
   ```

### If you see errors about missing modules:

```bash
cd ~/Sentry-AI
source venv/bin/activate
pip install -r requirements.txt
```

## Additional Notes

### Default Blacklist

If you remove `BLACKLIST_APPS` from your `.env`, Sentry-AI will use these defaults:

```python
blacklist_apps = [
    "Terminal",
    "iTerm",
    "Keychain Access",
    "System Preferences",
    "System Settings",
    "Activity Monitor",
    "Disk Utility",
]
```

### Adding More Apps to Blacklist

To blacklist additional apps:

```bash
# In your .env:
BLACKLIST_APPS=["Terminal","iTerm","Activity Monitor"]
```

Or use CSV format:
```bash
BLACKLIST_APPS=Terminal,iTerm,Activity Monitor
```

Both work now!

## Summary

✅ **Fixed:** JSON array parsing in `.env`  
✅ **Tested:** Terminal is now correctly blacklisted  
✅ **Ready:** Pull the fix and restart Sentry-AI  

The infinite loop should be completely resolved! 🎉
