"""
Main entry point for Sentry-AI.

This module orchestrates all the agents and starts the application.
"""

import sys
import time
from loguru import logger

from .core.config import settings
from .core.database import db_manager
from .agents import Observer, EventDrivenObserver, Analyzer, DecisionEngine, Actor, get_computer_use_agent
from .models.data_models import ObserverEvent, Action, ActionType


# Global system state
_system_state = {
    "is_running": False,
    "start_time": None,
    "observer_active": False,
    "ollama_available": False,
    "actions_performed_today": 0
}


class SentryAI:
    """Main application class that orchestrates all agents."""
    
    def __init__(self):
        """Initialize Sentry-AI and all its agents."""
        self.setup_logging()

        logger.info("=" * 60)
        logger.info(f"Initializing {settings.app_name} v{settings.app_version}")
        logger.info("=" * 60)

        # Initialize Computer Use Agent for vision-based automation
        try:
            self.computer_use_agent = get_computer_use_agent()
            self.use_computer_vision = True
            logger.info("🖥️  Computer Use Agent initialized - Vision AI enabled")
        except Exception as e:
            logger.warning(f"Computer Use Agent not available: {e}")
            logger.info("Falling back to traditional dialog detection")
            self.computer_use_agent = None
            self.use_computer_vision = False

        # Initialize agents
        self.analyzer = Analyzer()
        self.decision_engine = DecisionEngine(use_simple_vscode_strategy=settings.vscode_simple_mode)
        self.actor = Actor()

        # Choose observer type based on configuration
        if settings.event_driven_mode:
            logger.info("🚀 Using Event-Driven Observer (high performance mode)")
            self.observer = EventDrivenObserver(callback=self.on_dialog_detected)
        else:
            logger.info("⏱️  Using Polling Observer (legacy mode)")
            self.observer = Observer(callback=self.on_dialog_detected)

        self.is_running = False

        logger.info("All agents initialized successfully")
    
    def setup_logging(self):
        """Configure logging."""
        logger.remove()  # Remove default handler
        
        # Console handler
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=settings.log_level
        )
        
        # File handler
        logger.add(
            settings.log_file,
            rotation="10 MB",
            retention=f"{settings.log_retention_days} days",
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
        )
    
    def handle_dialog_with_vision(self, app_name: str):
        """
        Use Computer Use Agent to detect and handle dialogs with vision AI.

        Args:
            app_name: Name of the application

        Returns:
            True if dialog was handled successfully
        """
        if not self.use_computer_vision:
            return False

        try:
            # Check if VS Code dialog or Claude Code question is present
            task = f"""Look at the screen carefully. You are an AI assistant helping with VS Code automation.

IMPORTANT: Check for TWO types of interactions:

1. DIALOGS (Simple Yes/No):
   - Is there a dialog box asking for permission?
   - Example: "Allow this bash command?"
   - Action: Recommend "Yes" or "No" button

2. CLAUDE CODE QUESTIONS (Needs intelligent response):
   - Is Claude Code asking a question in the chat?
   - Example: "What should I name this function?"
   - Example: "Should I add error handling?"
   - Example: "Do you want comments in the code?"
   - Action: Provide a PROFESSIONAL, CONCISE answer to type

Respond with JSON:
{{
    "interaction_type": "dialog|question|none",
    "question": "the actual question being asked",
    "analysis": "what you see",
    "recommended_response": {{
        "type": "button|text|none",
        "action": "yes|no|<text to type>",
        "reasoning": "why this response"
    }}
}}

If Claude Code is asking a coding question:
- Give professional, concise answers
- Use best practices
- Be specific but brief
- Example: "Use 'calculate_fibonacci' for clarity"
- Example: "Yes, add try-except for file operations"

If NO interaction detected, set interaction_type to "none"."""

            logger.info(f"🔍 Analyzing screen for {app_name} interaction...")
            analysis = self.computer_use_agent.analyze_screen(task)

            # Get interaction type from new response format
            interaction_type = analysis.get('interaction_type', 'none')
            question = analysis.get('question', '')
            recommended_response = analysis.get('recommended_response', {})

            if interaction_type == 'none':
                logger.debug("No interaction detected by vision AI")
                return False

            logger.info(f"✅ Vision AI detected {interaction_type} in {app_name}")
            logger.info(f"📋 Question: {question[:100]}...")

            import pyautogui
            success = False
            chosen_option = ""

            # Handle QUESTIONS - Type intelligent response
            if interaction_type == 'question':
                response_text = recommended_response.get('action', '')
                reasoning = recommended_response.get('reasoning', '')

                if response_text and response_text not in ['yes', 'no']:
                    logger.info(f"🤖 AI Response: {response_text}")
                    logger.info(f"💭 Reasoning: {reasoning}")

                    # Type the intelligent response
                    time.sleep(0.5)
                    pyautogui.write(response_text, interval=0.03)
                    time.sleep(0.3)
                    pyautogui.press('return')

                    success = True
                    chosen_option = response_text
                    logger.success(f"✅ Typed and sent intelligent response")
                else:
                    logger.warning("No valid response text provided")
                    return False

            # Handle DIALOGS - Press ENTER/ESCAPE
            elif interaction_type == 'dialog':
                action_text = recommended_response.get('action', '').lower()

                keyboard_action = None
                if action_text in ['yes', 'ok', 'allow', 'continue', 'accept', 'approve']:
                    keyboard_action = 'return'
                    chosen_option = 'Yes'
                    logger.info("🎹 Using keyboard: ENTER (Accept)")
                elif action_text in ['no', 'cancel', 'deny']:
                    keyboard_action = 'escape'
                    chosen_option = 'No'
                    logger.info("🎹 Using keyboard: ESCAPE (Cancel)")

                if keyboard_action:
                    time.sleep(0.3)
                    pyautogui.press(keyboard_action)
                    success = True
                    logger.success(f"✅ Pressed {keyboard_action.upper()} key")
                else:
                    # Fallback to old behavior
                    action = analysis.get('recommended_action')
                    if action:
                        success = self.computer_use_agent.execute_action(action)
                        chosen_option = action.get('target', 'Unknown')

            if success:
                logger.success(f"🎯 Successfully automated {app_name} {interaction_type}")
                _system_state["actions_performed_today"] += 1

                # Log to database
                db_manager.log_action(
                    app_name=app_name,
                    window_title="Vision-based detection",
                    dialog_type=interaction_type,
                    question=question[:200],
                    options=[chosen_option],
                    chosen_option=chosen_option,
                    success=True,
                    execution_time_ms=0,
                    ai_confidence=analysis.get('confidence', 0.9),
                    ai_reasoning=recommended_response.get('reasoning', 'Vision AI analysis')
                )

                return True
            else:
                logger.error("Failed to execute vision-based action")
                return False

        except Exception as e:
            logger.error(f"Error in vision-based dialog handling: {e}")
            return False

    def on_dialog_detected(self, event: ObserverEvent):
        """
        Callback function called when the Observer detects a dialog.

        Args:
            event: The ObserverEvent containing dialog information
        """
        logger.info(f"Processing dialog from {event.app_name}")

        # Try vision-based handling first for VS Code
        if self.use_computer_vision and 'code' in event.app_name.lower():
            logger.info("🖥️  Attempting vision-based dialog detection...")
            if self.handle_dialog_with_vision(event.app_name):
                return

        try:
            # Step 1: Analyze the dialog
            context = self.analyzer.analyze(event.app_name, event.elements)
            
            if not context:
                logger.warning("Failed to analyze dialog")
                return
            
            # Step 2: Make a decision
            decision = self.decision_engine.decide(context)
            
            if not decision:
                logger.warning("Failed to make a decision")
                return
            
            # Step 3: Check if confirmation is required
            if decision.requires_confirmation:
                logger.info(
                    f"Confirmation required for {event.app_name}. "
                    f"Would choose: {decision.chosen_option}"
                )
                # TODO: Implement user confirmation UI
                return
            
            # Step 4: Find the target element
            target_element = self.actor.find_button_by_title(
                context.elements,
                decision.chosen_option
            )
            
            if not target_element:
                logger.error(f"Could not find button: {decision.chosen_option}")
                return
            
            # Step 5: Create and execute the action
            action = Action(
                action_type=ActionType.CLICK_BUTTON,
                target_element=target_element
            )
            
            # Measure execution time
            start_time = time.time()
            success = self.actor.execute(action)
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Log to database
            db_manager.log_action(
                app_name=event.app_name,
                window_title=context.window_title,
                dialog_type=context.dialog_type.value,
                question=context.question,
                options=context.options,
                chosen_option=decision.chosen_option,
                success=success,
                execution_time_ms=execution_time,
                ai_confidence=decision.confidence,
                ai_reasoning=decision.reasoning
            )
            
            if success:
                logger.success(
                    f"Successfully automated {event.app_name}: "
                    f"clicked '{decision.chosen_option}' ({execution_time:.1f}ms)"
                )
                _system_state["actions_performed_today"] += 1
            else:
                logger.error(f"Failed to execute action")
        
        except Exception as e:
            logger.error(f"Error processing dialog: {e}")
    
    def start(self):
        """Start Sentry-AI."""
        self.is_running = True

        logger.info("Starting Sentry-AI...")
        logger.info(f"Observer interval: {settings.observer_interval}s")
        logger.info(f"Ollama model: {settings.ollama_model}")
        logger.info(f"Blacklisted apps: {', '.join(settings.blacklist_apps)}")

        # If Computer Use Agent is available, start vision monitoring
        if self.use_computer_vision:
            logger.info("🖥️  Vision-based monitoring enabled")
            logger.info("Will automatically detect and handle VS Code dialogs")
            self._start_with_vision_monitoring()
        else:
            try:
                # Start the observer (blocking call)
                self.observer.start()
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.stop()

    def _start_with_vision_monitoring(self):
        """Start with periodic vision-based dialog checking."""
        import threading

        def vision_monitor_loop():
            """Periodically check for VS Code dialogs using vision."""
            logger.info("👁️  Vision monitor thread started")

            while self.is_running:
                try:
                    # Check if VS Code is active
                    from AppKit import NSWorkspace
                    workspace = NSWorkspace.sharedWorkspace()
                    active_app = workspace.frontmostApplication()

                    if active_app:
                        app_name = active_app.localizedName()

                        # Only check VS Code
                        if 'code' in app_name.lower():
                            self.handle_dialog_with_vision(app_name)

                    # Sleep for observer interval
                    time.sleep(settings.observer_interval)

                except Exception as e:
                    logger.error(f"Error in vision monitor loop: {e}")
                    time.sleep(settings.observer_interval)

        # Start vision monitor in background thread
        vision_thread = threading.Thread(target=vision_monitor_loop, daemon=True)
        vision_thread.start()

        # Also start traditional observer for fallback
        try:
            self.observer.start()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
    
    def stop(self):
        """Stop Sentry-AI."""
        logger.info("Stopping Sentry-AI...")
        self.is_running = False
        self.observer.stop()
        logger.info("Sentry-AI stopped")


def main():
    """Main function."""
    try:
        app = SentryAI()
        app.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
