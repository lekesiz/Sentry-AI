"""
macOS Menu Bar Application for Sentry-AI.

This module provides a native macOS menu bar interface for controlling
and monitoring Sentry-AI.
"""

import rumps
import threading
import time
from datetime import datetime
from typing import Optional
from pathlib import Path

from loguru import logger

from ..core.config import settings
from ..core.database import db_manager
from ..main import SentryAI


class SentryMenuBarApp(rumps.App):
    """
    macOS Menu Bar Application for Sentry-AI

    Provides:
    - Start/Stop control
    - Real-time status monitoring
    - Action statistics
    - Quick access to settings
    - Logs viewer
    """

    def __init__(self):
        super().__init__(
            name="Sentry-AI",
            icon=self._get_icon_path(),
            quit_button=None  # Custom quit handler
        )

        self.sentry_ai: Optional[SentryAI] = None
        self.sentry_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.stats = {"actions_today": 0, "actions_total": 0}

        self._setup_menu()
        self._start_status_updater()

    def _get_icon_path(self) -> Optional[str]:
        """Get path to menu bar icon"""
        # Try to find icon in resources
        icon_paths = [
            Path(__file__).parent.parent.parent / "resources" / "icon_small.png",
            Path(__file__).parent.parent.parent / "resources" / "icon.png",
        ]

        for icon_path in icon_paths:
            if icon_path.exists():
                return str(icon_path)

        # Return None to use text-based icon
        return None

    def _setup_menu(self):
        """Setup menu bar items"""
        # Status section
        self.status_item = rumps.MenuItem("Status: Stopped")
        self.menu.add(self.status_item)

        # Statistics section
        self.menu.add(rumps.separator)
        self.stats_item = rumps.MenuItem("Actions Today: 0")
        self.total_stats_item = rumps.MenuItem("Total Actions: 0")
        self.menu.add(self.stats_item)
        self.menu.add(self.total_stats_item)

        # Control section
        self.menu.add(rumps.separator)
        self.start_button = rumps.MenuItem(
            "Start Sentry-AI",
            callback=self.toggle_sentry
        )
        self.menu.add(self.start_button)

        # Mode indicator
        mode = "Event-Driven" if settings.event_driven_mode else "Polling"
        self.mode_item = rumps.MenuItem(f"Mode: {mode}")
        self.menu.add(self.mode_item)

        # Settings section
        self.menu.add(rumps.separator)
        settings_menu = rumps.MenuItem("Settings")

        # LLM Provider submenu
        provider_menu = rumps.MenuItem("LLM Provider")
        for provider in ["ollama", "gemini", "openai", "claude"]:
            is_current = settings.llm_provider == provider
            provider_item = rumps.MenuItem(
                f"{'✓ ' if is_current else ''}{provider.title()}",
                callback=lambda sender, p=provider: self.change_provider(p)
            )
            provider_menu.add(provider_item)

        settings_menu.add(provider_menu)

        # Observer mode toggle
        mode_toggle = rumps.MenuItem(
            f"{'✓ ' if settings.event_driven_mode else ''}Event-Driven Mode",
            callback=self.toggle_event_mode
        )
        settings_menu.add(mode_toggle)

        self.menu.add(settings_menu)

        # Tools section
        self.menu.add(rumps.separator)
        tools_menu = rumps.MenuItem("Tools")

        tools_menu.add(rumps.MenuItem(
            "View Logs",
            callback=self.open_logs
        ))

        tools_menu.add(rumps.MenuItem(
            "View Database",
            callback=self.open_database
        ))

        tools_menu.add(rumps.MenuItem(
            "Run Tests",
            callback=self.run_tests
        ))

        self.menu.add(tools_menu)

        # About & Quit
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("About Sentry-AI", callback=self.show_about))
        self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))

    def toggle_sentry(self, sender):
        """Start or stop Sentry-AI"""
        if not self.is_running:
            self.start_sentry()
        else:
            self.stop_sentry()

    def start_sentry(self):
        """Start Sentry-AI in background thread"""
        if self.is_running:
            rumps.notification(
                title="Sentry-AI",
                subtitle="Already Running",
                message="Sentry-AI is already active"
            )
            return

        try:
            logger.info("Starting Sentry-AI from menu bar...")

            # Create Sentry-AI instance
            self.sentry_ai = SentryAI()

            # Start in background thread
            self.sentry_thread = threading.Thread(
                target=self.sentry_ai.start,
                daemon=True
            )
            self.sentry_thread.start()

            self.is_running = True
            self.start_button.title = "Stop Sentry-AI"
            self.status_item.title = "Status: Running ✅"

            rumps.notification(
                title="Sentry-AI Started",
                subtitle="Now monitoring your Mac",
                message=f"Using {settings.llm_provider} provider"
            )

            logger.success("Sentry-AI started successfully")

        except Exception as e:
            logger.error(f"Failed to start Sentry-AI: {e}")
            rumps.alert(
                title="Error Starting Sentry-AI",
                message=str(e)
            )

    def stop_sentry(self):
        """Stop Sentry-AI"""
        if not self.is_running:
            return

        try:
            logger.info("Stopping Sentry-AI...")

            if self.sentry_ai:
                self.sentry_ai.stop()

            self.is_running = False
            self.start_button.title = "Start Sentry-AI"
            self.status_item.title = "Status: Stopped"

            rumps.notification(
                title="Sentry-AI Stopped",
                subtitle="Monitoring paused",
                message="Click Start to resume"
            )

            logger.info("Sentry-AI stopped")

        except Exception as e:
            logger.error(f"Error stopping Sentry-AI: {e}")

    def change_provider(self, provider: str):
        """Change LLM provider"""
        if self.is_running:
            rumps.alert(
                title="Cannot Change Provider",
                message="Please stop Sentry-AI before changing provider"
            )
            return

        settings.llm_provider = provider
        rumps.notification(
            title="Provider Changed",
            subtitle=f"Now using {provider.title()}",
            message="Restart Sentry-AI to apply changes"
        )

    def toggle_event_mode(self, sender):
        """Toggle event-driven mode"""
        if self.is_running:
            rumps.alert(
                title="Cannot Change Mode",
                message="Please stop Sentry-AI before changing mode"
            )
            return

        settings.event_driven_mode = not settings.event_driven_mode
        new_mode = "Event-Driven" if settings.event_driven_mode else "Polling"

        self.mode_item.title = f"Mode: {new_mode}"

        rumps.notification(
            title="Mode Changed",
            subtitle=f"Now using {new_mode} mode",
            message="Restart Sentry-AI to apply changes"
        )

    def open_logs(self, sender):
        """Open log file in Console.app"""
        import subprocess

        log_path = Path(settings.log_file).absolute()

        if log_path.exists():
            subprocess.run(["open", "-a", "Console", str(log_path)])
        else:
            rumps.alert(
                title="Log File Not Found",
                message=f"No log file at {log_path}"
            )

    def open_database(self, sender):
        """Open database in DB Browser"""
        import subprocess

        db_path = Path("sentry_ai.db").absolute()

        if db_path.exists():
            # Try to open with DB Browser for SQLite
            subprocess.run(["open", str(db_path)])
        else:
            rumps.alert(
                title="Database Not Found",
                message=f"No database at {db_path}"
            )

    def run_tests(self, sender):
        """Run user testing framework"""
        import subprocess

        rumps.notification(
            title="Running Tests",
            subtitle="This may take a few minutes",
            message="Check terminal for progress"
        )

        try:
            subprocess.Popen([
                "python",
                "user_testing_framework.py"
            ])
        except Exception as e:
            rumps.alert(
                title="Error Running Tests",
                message=str(e)
            )

    def show_about(self, sender):
        """Show about dialog"""
        rumps.alert(
            title=f"Sentry-AI v{settings.app_version}",
            message=(
                "Cognitive Automation Agent for macOS\n\n"
                f"LLM Provider: {settings.llm_provider}\n"
                f"Observer Mode: {'Event-Driven' if settings.event_driven_mode else 'Polling'}\n\n"
                "Developed by Mikail Lekesiz\n"
                "https://github.com/lekesiz/Sentry-AI"
            )
        )

    def quit_app(self, sender):
        """Quit the application"""
        if self.is_running:
            response = rumps.alert(
                title="Sentry-AI is Running",
                message="Are you sure you want to quit?",
                ok="Quit",
                cancel="Cancel"
            )

            if response == 0:  # Cancel
                return

            self.stop_sentry()

        rumps.quit_application()

    def _start_status_updater(self):
        """Start background thread to update statistics"""
        def update_stats():
            while True:
                try:
                    # Get statistics from database
                    stats = db_manager.get_today_stats()

                    if stats:
                        self.stats["actions_today"] = stats.get("count", 0)

                    total_stats = db_manager.get_total_stats()
                    if total_stats:
                        self.stats["actions_total"] = total_stats.get("count", 0)

                    # Update menu items
                    self.stats_item.title = f"Actions Today: {self.stats['actions_today']}"
                    self.total_stats_item.title = f"Total Actions: {self.stats['actions_total']}"

                except Exception as e:
                    logger.debug(f"Error updating stats: {e}")

                time.sleep(10)  # Update every 10 seconds

        updater_thread = threading.Thread(target=update_stats, daemon=True)
        updater_thread.start()


def run_menubar_app():
    """Run the menu bar application"""
    logger.info("Starting Sentry-AI Menu Bar App...")

    try:
        app = SentryMenuBarApp()
        app.run()
    except Exception as e:
        logger.error(f"Error running menu bar app: {e}")
        raise


if __name__ == "__main__":
    run_menubar_app()
