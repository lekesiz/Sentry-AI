#!/bin/bash
# Sentry-AI Setup Script
# This script automates the installation and setup process

echo "🚀 Sentry-AI Setup Script"
echo "========================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Warning: This project is designed for macOS"
    echo "   Some features may not work on other platforms"
    echo ""
fi

# Check Python version
echo "1️⃣  Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "   Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "   ✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "2️⃣  Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate
echo "   ✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "4️⃣  Upgrading pip..."
pip install --upgrade pip setuptools wheel -q
echo "   ✓ pip, setuptools, and wheel upgraded"
echo ""

# Install dependencies
echo "5️⃣  Installing dependencies..."
echo "   This may take a few minutes..."
echo ""

# Try to install PyObjC first (requires Xcode)
echo "   📦 Attempting to install PyObjC (requires Xcode)..."
PYOBJC_INSTALL_LOG=$(mktemp)

if pip install pyobjc-core==10.3.1 > "$PYOBJC_INSTALL_LOG" 2>&1; then
    echo "   ✓ PyObjC core installed successfully"
    pip install pyobjc-framework-Cocoa==10.3.1 pyobjc-framework-Quartz==10.3.1 pyobjc-framework-ApplicationServices==10.3.1 pyobjc-framework-Vision==10.3.1 -q
    echo "   ✓ PyObjC frameworks installed"
    PYOBJC_INSTALLED=true
else
    echo "   ⚠️  PyObjC installation failed"
    echo ""
    echo "   This is likely because Xcode is not installed or not configured properly."
    echo ""
    echo "   📖 To fix this, you have two options:"
    echo ""
    echo "   Option A: Install Xcode (Recommended for full functionality)"
    echo "   ────────────────────────────────────────────────────────────"
    echo "   1. Open App Store"
    echo "   2. Search for 'Xcode'"
    echo "   3. Click 'Get' or 'Install' (~8-12 GB download)"
    echo "   4. Once installed, open Xcode once to complete setup"
    echo "   5. Run this setup script again"
    echo ""
    echo "   📚 See XCODE_SETUP.md for detailed instructions"
    echo ""
    echo "   Option B: Continue with Browser API only (No Xcode needed)"
    echo "   ──────────────────────────────────────────────────────────"
    echo "   - Works with VS Code web (vscode.dev, github.dev)"
    echo "   - Does NOT work with native macOS applications"
    echo ""
    
    # Ask user what to do
    read -p "   Would you like to continue with Browser API only? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "   📦 Installing minimal dependencies (without PyObjC)..."
        
        # Install all dependencies except PyObjC
        pip install fastapi==0.115.5 -q
        pip install "uvicorn[standard]==0.32.1" -q
        pip install pydantic==2.10.3 -q
        pip install pydantic-settings==2.6.1 -q
        pip install ollama==0.4.4 -q
        pip install google-genai==1.9.0 -q
        pip install openai==1.57.2 -q
        pip install anthropic==0.42.0 -q
        pip install sqlalchemy==2.0.36 -q
        pip install alembic==1.14.0 -q
        pip install python-dotenv==1.0.1 -q
        pip install loguru==0.7.2 -q
        pip install pillow==11.0.0 -q
        pip install pytest==8.3.4 -q
        pip install pytest-asyncio==0.24.0 -q
        pip install pytest-cov==6.0.0 -q
        pip install pytest-mock==3.14.0 -q
        pip install black==24.10.0 -q
        pip install flake8==7.1.1 -q
        pip install mypy==1.13.0 -q
        pip install pre-commit==4.0.1 -q
        
        echo "   ✓ Minimal dependencies installed"
        echo ""
        echo "   ⚠️  Note: Only Browser API will be available"
        echo "   ⚠️  Native macOS automation requires Xcode + PyObjC"
        
        PYOBJC_INSTALLED=false
    else
        echo ""
        echo "   ❌ Installation cancelled"
        echo ""
        echo "   Please install Xcode and run this script again."
        echo "   See XCODE_SETUP.md for detailed instructions."
        rm "$PYOBJC_INSTALL_LOG"
        exit 1
    fi
fi

rm "$PYOBJC_INSTALL_LOG"

# Install remaining dependencies
if [ "$PYOBJC_INSTALLED" = true ]; then
    echo ""
    echo "   📦 Installing remaining dependencies..."
    pip install -r requirements.txt -q 2>&1 | grep -v "Requirement already satisfied" || true
    echo "   ✓ All dependencies installed"
fi

echo ""

# Check Ollama installation
echo "6️⃣  Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "   ✓ Ollama is installed"
    
    # Check if Ollama is running
    if ollama list &> /dev/null; then
        echo "   ✓ Ollama server is running"
        
        # Check if phi3:mini is available
        if ollama list | grep -q "phi3:mini"; then
            echo "   ✓ Model phi3:mini is available"
        else
            echo "   ⚠️  Model phi3:mini not found"
            echo "   Run: ollama pull phi3:mini"
        fi
    else
        echo "   ⚠️  Ollama server is not running"
        echo "   Run: ollama serve"
    fi
else
    echo "   ⚠️  Ollama is not installed"
    echo "   Install with: brew install ollama"
fi
echo ""

# Create .env file if it doesn't exist
echo "7️⃣  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    
    # If PyObjC is not installed, configure for Browser API only
    if [ "$PYOBJC_INSTALLED" = false ]; then
        echo "USE_ACCESSIBILITY_API=False" >> .env
        echo "USE_BROWSER_API=True" >> .env
    fi
    
    echo "   ✓ Created .env file from .env.example"
    echo "   📝 You can customize settings in .env"
else
    echo "   ✓ .env file already exists"
    
    # Update .env if PyObjC is not installed
    if [ "$PYOBJC_INSTALLED" = false ]; then
        if ! grep -q "USE_ACCESSIBILITY_API" .env; then
            echo "USE_ACCESSIBILITY_API=False" >> .env
            echo "USE_BROWSER_API=True" >> .env
            echo "   ✓ Updated .env for Browser API mode"
        fi
    fi
fi
echo ""

# Run installation test
echo "8️⃣  Running installation test..."
if python test_installation.py 2>&1; then
    echo "   ✓ Installation test passed"
else
    echo "   ⚠️  Some tests failed (this is OK if PyObjC is not installed)"
fi
echo ""

# Print next steps
echo "✅ Setup Complete!"
echo ""

if [ "$PYOBJC_INSTALLED" = true ]; then
    echo "📋 Next Steps:"
    echo "   1. Make sure Ollama is running: ollama serve"
    echo "   2. Download the AI model: ollama pull phi3:mini"
    echo "   3. Grant Accessibility permissions to your Terminal:"
    echo "      System Settings > Privacy & Security > Accessibility"
    echo "   4. Run Sentry-AI: make run"
else
    echo "📋 Next Steps (Browser API Mode):"
    echo "   1. Make sure Ollama is running: ollama serve"
    echo "   2. Download the AI model: ollama pull phi3:mini"
    echo "   3. Open VS Code web (vscode.dev or github.dev)"
    echo "   4. Run Sentry-AI: make run"
    echo ""
    echo "   💡 To enable native macOS automation:"
    echo "      - Install Xcode (see XCODE_SETUP.md)"
    echo "      - Run this setup script again"
fi

echo ""
echo "📚 Documentation:"
echo "   - Xcode Setup: XCODE_SETUP.md"
echo "   - Quick Start: QUICKSTART.md"
echo "   - Testing Guide: TESTING_GUIDE.md"
echo "   - Full Documentation: README.md"
echo ""
echo "🎉 Happy automating!"
