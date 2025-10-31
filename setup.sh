#!/bin/bash
# Sentry-AI Setup Script
# This script automates the installation and setup process

set -e  # Exit on error

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
pip install --upgrade pip -q
echo "   ✓ pip upgraded"
echo ""

# Install dependencies
echo "5️⃣  Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt -q
echo "   ✓ Dependencies installed"
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
    echo "   ✓ Created .env file from .env.example"
    echo "   📝 You can customize settings in .env"
else
    echo "   ✓ .env file already exists"
fi
echo ""

# Run installation test
echo "8️⃣  Running installation test..."
python test_installation.py
echo ""

# Print next steps
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Make sure Ollama is running: ollama serve"
echo "   2. Download the AI model: ollama pull phi3:mini"
echo "   3. Grant Accessibility permissions to your Terminal"
echo "   4. Run Sentry-AI: make run"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: QUICKSTART.md"
echo "   - Testing Guide: TESTING_GUIDE.md"
echo "   - Full Documentation: README.md"
echo ""
echo "🎉 Happy automating!"
