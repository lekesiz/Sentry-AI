#!/usr/bin/env python3
"""
Launch Sentry-AI Menu Bar Application

This script starts the native macOS menu bar interface for Sentry-AI.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sentry_ai.ui import run_menubar_app

if __name__ == "__main__":
    run_menubar_app()
