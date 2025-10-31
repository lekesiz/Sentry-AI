#!/usr/bin/env python3
"""
VS Code Automation Example for Sentry-AI.

This example demonstrates how to use Sentry-AI to automate Claude Code dialogs in VS Code.
"""

import time
from loguru import logger

from sentry_ai.agents.vscode_observer import VSCodeObserver
from sentry_ai.agents.decision_engine import DecisionEngine
from sentry_ai.agents.actor import Actor
from sentry_ai.models.data_models import Action, ActionType


def main():
    """Main automation loop."""
    logger.info("Starting VS Code automation example")
    
    # Initialize components
    observer = VSCodeObserver()
    decision_engine = DecisionEngine()
    actor = Actor()
    
    # Check if VS Code is running
    if not observer.is_vscode_running():
        logger.warning("VS Code is not running. Please start VS Code and try again.")
        return
    
    logger.info("VS Code detected. Starting automation...")
    
    # Main loop
    try:
        while True:
            # Detect Claude dialogs
            dialog = observer.detect_claude_dialog()
            
            if dialog:
                logger.info(f"Dialog detected: {dialog.question}")
                logger.info(f"Options: {dialog.options}")
                
                # Make decision
                decision = decision_engine.decide(dialog)
                
                if decision:
                    logger.info(f"Decision: {decision.chosen_option}")
                    logger.info(f"Reasoning: {decision.reasoning}")
                    logger.info(f"Confidence: {decision.confidence}")
                    
                    # Check if confirmation is required
                    if decision.requires_confirmation:
                        response = input(f"\nConfirm action '{decision.chosen_option}'? (y/n): ")
                        if response.lower() != 'y':
                            logger.info("Action cancelled by user")
                            continue
                    
                    # Execute action
                    if decision.chosen_option in (dialog.options or []):
                        # Click button
                        button = actor.find_button_by_title(dialog.elements, decision.chosen_option)
                        if button:
                            action = Action(
                                action_type=ActionType.CLICK_BUTTON,
                                target_element=button,
                                parameters={}
                            )
                            success = actor.execute(action)
                            logger.info(f"Action executed: {success}")
                        else:
                            logger.warning(f"Button not found: {decision.chosen_option}")
                    else:
                        # Type text (for questions)
                        logger.info(f"Typing text: {decision.chosen_option[:50]}...")
                        # Note: Text typing requires finding the focused text field
                        # This is a simplified example
                        action = Action(
                            action_type=ActionType.TYPE_TEXT,
                            target_element=None,  # Will use focused element
                            parameters={"text": decision.chosen_option}
                        )
                        success = actor.execute(action)
                        logger.info(f"Text typed: {success}")
                else:
                    logger.warning("No decision made for dialog")
            
            # Wait before next check
            time.sleep(1.0)
    
    except KeyboardInterrupt:
        logger.info("Automation stopped by user")
    except Exception as e:
        logger.error(f"Error in automation loop: {e}")


if __name__ == "__main__":
    main()
