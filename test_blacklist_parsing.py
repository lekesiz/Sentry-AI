#!/usr/bin/env python3
"""
Test script to verify blacklist parsing from .env file.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_blacklist_parsing():
    """Test that blacklist is parsed correctly from .env"""
    
    print("=" * 60)
    print("Testing Blacklist Parsing")
    print("=" * 60)
    
    # Import after adding to path
    from sentry_ai.core.config import settings, is_app_allowed
    
    print(f"\n1. Blacklist Apps: {settings.blacklist_apps}")
    print(f"   Type: {type(settings.blacklist_apps)}")
    
    if settings.blacklist_apps:
        print(f"   First element: '{settings.blacklist_apps[0]}'")
        print(f"   First element type: {type(settings.blacklist_apps[0])}")
    
    print(f"\n2. LLM Fallback Order: {settings.llm_fallback_order}")
    print(f"   Type: {type(settings.llm_fallback_order)}")
    
    print("\n3. Testing is_app_allowed():")
    test_apps = ["Terminal", "TextEdit", "Safari", "iTerm"]
    
    for app in test_apps:
        allowed = is_app_allowed(app)
        status = "❌ BLOCKED" if not allowed else "✅ ALLOWED"
        print(f"   {app}: {status}")
    
    print("\n4. Expected Results:")
    print("   Terminal: ❌ BLOCKED (in default blacklist)")
    print("   TextEdit: ✅ ALLOWED")
    print("   Safari: ✅ ALLOWED")
    print("   iTerm: ❌ BLOCKED (in default blacklist)")
    
    # Verify Terminal is blocked
    if not is_app_allowed("Terminal"):
        print("\n✅ SUCCESS: Terminal is correctly blacklisted!")
        return True
    else:
        print("\n❌ FAILURE: Terminal is NOT blacklisted!")
        print("   This means the parsing is still broken.")
        return False

if __name__ == "__main__":
    try:
        success = test_blacklist_parsing()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
