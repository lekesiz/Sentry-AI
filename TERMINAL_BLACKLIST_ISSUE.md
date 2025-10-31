# Terminal Blacklist Issue Analysis

## Problem

Sentry-AI is detecting Terminal dialogs in an infinite loop despite Terminal being in the blacklist.

## Root Cause Analysis

### 1. **Blacklist Configuration Issue**

From the screenshots, we can see:
- User's `.env` has: `BLACKLIST_APPS=["Terminal"]`
- Default config has: `blacklist_apps: List[str] = Field(default=["Terminal", "iTerm", ...])`

**The problem:** Pydantic is not parsing the JSON array from `.env` correctly!

### 2. **Why It's Failing**

When Pydantic reads `BLACKLIST_APPS=["Terminal"]` from `.env`, it treats it as a **string**, not a list!

So `settings.blacklist_apps` becomes:
```python
['["Terminal"]']  # A list with ONE string element
```

Instead of:
```python
['Terminal']  # A list with "Terminal" as element
```

### 3. **Verification in Logs**

From the screenshots:
```
Dialog detected in Terminal
Processing dialog from Terminal
Failed to analyze dialog
```

This confirms that `is_app_allowed("Terminal")` is returning `True` because:
```python
if app_name in settings.blacklist_apps:  # "Terminal" in ['["Terminal"]'] = False!
    return False
```

## Solution

### Option 1: Fix Pydantic Parsing (Recommended)

Add a custom validator to parse JSON strings:

```python
from pydantic import field_validator
import json

class Settings(BaseSettings):
    blacklist_apps: List[str] = Field(default=["Terminal", ...])
    
    @field_validator('blacklist_apps', 'llm_fallback_order', mode='before')
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]  # Fallback to single item list
        return v
```

### Option 2: Update .env Format

Change `.env` to use comma-separated values:
```bash
BLACKLIST_APPS=Terminal,iTerm,Keychain Access
```

Then update Settings:
```python
@field_validator('blacklist_apps', mode='before')
@classmethod
def parse_csv(cls, v):
    if isinstance(v, str):
        return [x.strip() for x in v.split(',')]
    return v
```

### Option 3: Use Default Blacklist

Remove `BLACKLIST_APPS` from `.env` entirely and rely on the default:
```python
blacklist_apps: List[str] = Field(
    default=["Terminal", "iTerm", "Keychain Access", ...]
)
```

## Recommended Fix

**Use Option 1** because:
1. JSON format is already documented in `.env.example`
2. It's consistent with `LLM_FALLBACK_ORDER` format
3. No breaking changes for users

## Implementation

1. Add `field_validator` to `Settings` class
2. Apply to both `blacklist_apps` and `llm_fallback_order`
3. Test with user's `.env` configuration
4. Push fix to GitHub
5. User runs `git pull` and restarts

## Testing

After fix, verify:
```bash
cd ~/Sentry-AI
source venv/bin/activate
python -c "from sentry_ai.core.config import settings; print(settings.blacklist_apps)"
# Should output: ['Terminal']
# NOT: ['["Terminal"]']
```
