#!/usr/bin/env python3
"""
Test Computer Use Agent

Quick test to see if computer use agent works
"""

from sentry_ai.agents import get_computer_use_agent
from loguru import logger

def main():
    logger.info("🚀 Testing Computer Use Agent")

    # Get agent
    agent = get_computer_use_agent()

    # Test 1: Take screenshot
    logger.info("📸 Test 1: Taking screenshot...")
    screenshot = agent.capture_screen()
    logger.success(f"✅ Screenshot captured: {screenshot.size}")

    # Test 2: Analyze screen
    logger.info("🤖 Test 2: Analyzing screen...")
    analysis = agent.analyze_screen("What applications are currently visible on screen?")
    logger.success(f"✅ Analysis complete")
    logger.info(f"Analysis: {analysis.get('analysis', '')[:200]}...")

    # Test 3: Look for VS Code
    logger.info("🔍 Test 3: Looking for VS Code...")
    vs_code_check = agent.analyze_screen("Is Visual Studio Code open? If yes, where is it on screen?")
    logger.success(f"✅ VS Code check complete")
    logger.info(f"Result: {vs_code_check.get('analysis', '')[:200]}...")

    logger.success("🎉 All tests passed!")

if __name__ == "__main__":
    main()
