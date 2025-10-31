#!/usr/bin/env python3
"""
Test all LLM providers in parallel to see which one works.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sentry_ai.core.llm_provider import (
    OllamaProvider,
    GeminiProvider,
    OpenAIProvider,
    ClaudeProvider
)

def test_provider(name, provider):
    """Test a single LLM provider."""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    
    try:
        # Check availability
        if not provider.is_available():
            print(f"❌ {name}: Not available")
            return False
        
        print(f"✅ {name}: Available")
        
        # Test simple generation
        prompt = "Say 'Hello' in one word only."
        print(f"\nPrompt: {prompt}")
        
        response = provider.generate(prompt)
        print(f"Response: {response}")
        
        # Test structured generation (like dialog analysis)
        print(f"\n--- Testing structured generation ---")
        options = ["Save", "Don't Save", "Cancel"]
        structured_prompt = "A user is closing a document with unsaved changes. What should we do?"
        
        result = provider.generate_structured(
            structured_prompt,
            options,
            system_prompt="You are a helpful assistant that analyzes dialogs."
        )
        
        print(f"Choice: {result.get('choice')}")
        print(f"Reasoning: {result.get('reasoning')}")
        print(f"Confidence: {result.get('confidence')}")
        
        print(f"\n✅ {name}: SUCCESS!")
        return True
        
    except Exception as e:
        print(f"\n❌ {name}: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test all LLM providers."""
    print("="*60)
    print("Testing All LLM Providers")
    print("="*60)
    
    # Get API keys from environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"\nAPI Keys Status:")
    print(f"  Gemini: {'✅ Set' if gemini_key else '❌ Not set'}")
    print(f"  OpenAI: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"  Claude: {'✅ Set' if anthropic_key else '❌ Not set'}")
    
    # Initialize providers
    providers = {
        "Ollama": OllamaProvider(model="phi3:mini"),
        "Gemini": GeminiProvider(model="gemini-2.0-flash-exp"),
        "OpenAI": OpenAIProvider(model="gpt-4o-mini"),
        "Claude": ClaudeProvider(model="claude-3-5-sonnet-20241022")
    }
    
    # Test each provider
    results = {}
    for name, provider in providers.items():
        results[name] = test_provider(name, provider)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    working = [name for name, success in results.items() if success]
    failed = [name for name, success in results.items() if not success]
    
    if working:
        print(f"\n✅ Working providers ({len(working)}):")
        for name in working:
            print(f"   - {name}")
    
    if failed:
        print(f"\n❌ Failed providers ({len(failed)}):")
        for name in failed:
            print(f"   - {name}")
    
    if working:
        print(f"\n🎯 Recommended: Use {working[0]}")
        print(f"\n💡 Update your .env:")
        print(f"   LLM_PROVIDER={working[0].lower()}")
    else:
        print(f"\n⚠️  No working providers found!")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check API keys in .env")
        print(f"   2. Make sure Ollama is running: ollama serve")
        print(f"   3. Check internet connection for cloud providers")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
