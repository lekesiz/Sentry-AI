"""
Main entry point for Sentry-AI.

This module orchestrates all the agents and starts the application.
"""

import sys
import time
from loguru import logger

from .core.config import settings
from .core.database import db_manager
from .agents import Observer, EventDrivenObserver, Analyzer, DecisionEngine, Actor
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
        
        # Initialize agents
        self.analyzer = Analyzer()
        self.decision_engine = DecisionEngine()
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
    
    def on_dialog_detected(self, event: ObserverEvent):
        """
        Callback function called when the Observer detects a dialog.
        
        Args:
            event: The ObserverEvent containing dialog information
        """
        logger.info(f"Processing dialog from {event.app_name}")
        
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
        
        try:
            # Start the observer (blocking call)
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
