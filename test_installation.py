#!/usr/bin/env python3
"""
Test script to verify Sentry-AI installation.

This script checks if all dependencies are installed correctly
and if the basic modules can be imported.
"""

import sys

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing Sentry-AI installation...\n")
    
    errors = []
    warnings = []
    
    # Test core dependencies
    print("1. Testing core dependencies...")
    try:
        import pydantic
        print("   ✓ pydantic")
    except ImportError as e:
        errors.append(f"pydantic: {e}")
        print(f"   ✗ pydantic: {e}")
    
    try:
        from pydantic_settings import BaseSettings
        print("   ✓ pydantic-settings")
    except ImportError as e:
        errors.append(f"pydantic-settings: {e}")
        print(f"   ✗ pydantic-settings: {e}")
    
    try:
        import loguru
        print("   ✓ loguru")
    except ImportError as e:
        errors.append(f"loguru: {e}")
        print(f"   ✗ loguru: {e}")
    
    try:
        import sqlalchemy
        print("   ✓ sqlalchemy")
    except ImportError as e:
        errors.append(f"sqlalchemy: {e}")
        print(f"   ✗ sqlalchemy: {e}")
    
    try:
        import fastapi
        print("   ✓ fastapi")
    except ImportError as e:
        errors.append(f"fastapi: {e}")
        print(f"   ✗ fastapi: {e}")
    
    try:
        import uvicorn
        print("   ✓ uvicorn")
    except ImportError as e:
        errors.append(f"uvicorn: {e}")
        print(f"   ✗ uvicorn: {e}")
    
    # Test macOS frameworks (optional)
    print("\n2. Testing macOS frameworks (optional)...")
    try:
        from Foundation import NSObject
        print("   ✓ pyobjc-core (Foundation)")
    except ImportError as e:
        warnings.append(f"pyobjc-core: {e}")
        print(f"   ⚠ pyobjc-core: Not available (macOS only)")
    
    try:
        from AppKit import NSApplication
        print("   ✓ pyobjc-framework-Cocoa")
    except ImportError as e:
        warnings.append(f"pyobjc-framework-Cocoa: {e}")
        print(f"   ⚠ pyobjc-framework-Cocoa: Not available (macOS only)")
    
    try:
        from Quartz import CGWindowListCreateImage
        print("   ✓ pyobjc-framework-Quartz")
    except ImportError as e:
        warnings.append(f"pyobjc-framework-Quartz: {e}")
        print(f"   ⚠ pyobjc-framework-Quartz: Not available (macOS only)")
    
    try:
        from Vision import VNRecognizeTextRequest
        print("   ✓ pyobjc-framework-Vision")
    except ImportError as e:
        warnings.append(f"pyobjc-framework-Vision: {e}")
        print(f"   ⚠ pyobjc-framework-Vision: Not available (macOS only)")
    
    # Test Ollama (optional)
    print("\n3. Testing Ollama integration (optional)...")
    try:
        import ollama
        print("   ✓ ollama")
        try:
            ollama.list()
            print("   ✓ Ollama server is running")
        except Exception as e:
            warnings.append(f"Ollama server: {e}")
            print(f"   ⚠ Ollama server not running: {e}")
    except ImportError as e:
        warnings.append(f"ollama: {e}")
        print(f"   ⚠ ollama: {e}")
    
    # Test Sentry-AI modules
    print("\n4. Testing Sentry-AI modules...")
    try:
        from sentry_ai.core.config import settings
        print("   ✓ sentry_ai.core.config")
    except Exception as e:
        errors.append(f"sentry_ai.core.config: {e}")
        print(f"   ✗ sentry_ai.core.config: {e}")
    
    try:
        from sentry_ai.models.data_models import UIElement
        print("   ✓ sentry_ai.models.data_models")
    except Exception as e:
        errors.append(f"sentry_ai.models.data_models: {e}")
        print(f"   ✗ sentry_ai.models.data_models: {e}")
    
    try:
        from sentry_ai.agents import Observer, Analyzer, DecisionEngine, Actor
        print("   ✓ sentry_ai.agents")
    except Exception as e:
        errors.append(f"sentry_ai.agents: {e}")
        print(f"   ✗ sentry_ai.agents: {e}")
    
    try:
        from sentry_ai.core.database import db_manager
        print("   ✓ sentry_ai.core.database")
    except Exception as e:
        errors.append(f"sentry_ai.core.database: {e}")
        print(f"   ✗ sentry_ai.core.database: {e}")
    
    try:
        from sentry_ai.api.routes import app
        print("   ✓ sentry_ai.api.routes")
    except Exception as e:
        errors.append(f"sentry_ai.api.routes: {e}")
        print(f"   ✗ sentry_ai.api.routes: {e}")
    
    # Print summary
    print("\n" + "="*60)
    if errors:
        print(f"❌ FAILED: {len(errors)} critical error(s) found:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease run: pip install -r requirements.txt")
        return False
    else:
        print("✅ SUCCESS: All critical dependencies are installed!")
        
        if warnings:
            print(f"\n⚠️  {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"   - {warning}")
            print("\nThese are optional and only needed on macOS.")
        
        print("\nSentry-AI is ready to use!")
        print("Run: python -m sentry_ai.main")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
