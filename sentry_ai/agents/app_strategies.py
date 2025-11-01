"""
Application-Specific Strategies for Sentry-AI

This module contains specialized decision strategies for different macOS applications.
Each strategy understands the specific dialogs and workflows of its target application.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger


class AppStrategyType(Enum):
    """Types of application strategies"""
    SAVE_DIALOG = "save_dialog"
    QUIT_CONFIRMATION = "quit_confirmation"
    DELETE_CONFIRMATION = "delete_confirmation"
    DOWNLOAD_DIALOG = "download_dialog"
    PERMISSION_REQUEST = "permission_request"
    UPDATE_NOTIFICATION = "update_notification"
    FILE_CONFLICT = "file_conflict"


@dataclass
class StrategyDecision:
    """Decision made by an application strategy"""
    chosen_option: str
    confidence: float
    reasoning: str
    requires_confirmation: bool = False


class BaseAppStrategy:
    """Base class for application-specific strategies"""

    def __init__(self, app_name: str):
        self.app_name = app_name

    def can_handle(self, context: Dict[str, Any]) -> bool:
        """
        Check if this strategy can handle the given context

        Args:
            context: Dialog context

        Returns:
            True if this strategy can handle the dialog
        """
        raise NotImplementedError

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """
        Make a decision for the dialog

        Args:
            context: Dialog context

        Returns:
            StrategyDecision or None if cannot decide
        """
        raise NotImplementedError


class TextEditStrategy(BaseAppStrategy):
    """Strategy for TextEdit application"""

    def __init__(self):
        super().__init__("TextEdit")

    def can_handle(self, context: Dict[str, Any]) -> bool:
        """Check if this is a TextEdit dialog"""
        return context.get("app_name") == "TextEdit"

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """Decide on TextEdit dialogs"""
        dialog_type = context.get("dialog_type")
        question = context.get("question", "").lower()
        options = context.get("options", [])

        # Save dialog when closing unsaved document
        if "save" in question and "don't save" in [o.lower() for o in options]:
            # If document is empty or trivial, don't save
            # Otherwise, save by default for safety
            return StrategyDecision(
                chosen_option="Save",
                confidence=0.8,
                reasoning="Default to saving documents in TextEdit for safety",
                requires_confirmation=False
            )

        return None


class FinderStrategy(BaseAppStrategy):
    """Strategy for Finder application"""

    def __init__(self):
        super().__init__("Finder")

    def can_handle(self, context: Dict[str, Any]) -> bool:
        return context.get("app_name") == "Finder"

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """Decide on Finder dialogs"""
        question = context.get("question", "").lower()

        # Delete/Trash confirmation - require user confirmation
        if any(word in question for word in ["delete", "remove", "trash", "empty"]):
            return StrategyDecision(
                chosen_option="Cancel",
                confidence=0.9,
                reasoning="Destructive Finder operations require user confirmation",
                requires_confirmation=True
            )

        # File replacement
        if "replace" in question:
            return StrategyDecision(
                chosen_option="Cancel",
                confidence=0.8,
                reasoning="File replacement should be confirmed by user",
                requires_confirmation=True
            )

        return None


class SafariStrategy(BaseAppStrategy):
    """Strategy for Safari browser"""

    def __init__(self):
        super().__init__("Safari")

    def can_handle(self, context: Dict[str, Any]) -> bool:
        return context.get("app_name") == "Safari"

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """Decide on Safari dialogs"""
        question = context.get("question", "").lower()

        # Download confirmation
        if "download" in question:
            return StrategyDecision(
                chosen_option="Allow",
                confidence=0.7,
                reasoning="Auto-allow downloads in Safari",
                requires_confirmation=False
            )

        # Close tabs confirmation
        if "close" in question and "tab" in question:
            return StrategyDecision(
                chosen_option="Close",
                confidence=0.6,
                reasoning="Allow closing multiple tabs",
                requires_confirmation=False
            )

        # Clear history/data
        if any(word in question for word in ["clear", "remove", "delete"]):
            return StrategyDecision(
                chosen_option="Cancel",
                confidence=0.9,
                reasoning="Clearing browsing data requires confirmation",
                requires_confirmation=True
            )

        return None


class MailStrategy(BaseAppStrategy):
    """Strategy for Mail.app"""

    def __init__(self):
        super().__init__("Mail")

    def can_handle(self, context: Dict[str, Any]) -> bool:
        return context.get("app_name") == "Mail"

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """Decide on Mail dialogs"""
        question = context.get("question", "").lower()

        # Delete email confirmation
        if "delete" in question:
            return StrategyDecision(
                chosen_option="Delete",
                confidence=0.7,
                reasoning="Allow deleting emails (can be recovered from trash)",
                requires_confirmation=False
            )

        # Send email without subject
        if "subject" in question and "send" in question:
            return StrategyDecision(
                chosen_option="Don't Send",
                confidence=0.8,
                reasoning="Don't send emails without subject",
                requires_confirmation=False
            )

        # Attach large files
        if "large" in question or "size" in question:
            return StrategyDecision(
                chosen_option="Send",
                confidence=0.6,
                reasoning="Allow sending large attachments",
                requires_confirmation=True
            )

        return None


class NotesStrategy(BaseAppStrategy):
    """Strategy for Notes.app"""

    def __init__(self):
        super().__init__("Notes")

    def can_handle(self, context: Dict[str, Any]) -> bool:
        return context.get("app_name") == "Notes"

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """Decide on Notes dialogs"""
        question = context.get("question", "").lower()

        # Delete note confirmation
        if "delete" in question:
            return StrategyDecision(
                chosen_option="Delete",
                confidence=0.7,
                reasoning="Allow deleting notes (recoverable from Recently Deleted)",
                requires_confirmation=False
            )

        # Save changes
        if "save" in question:
            return StrategyDecision(
                chosen_option="Save",
                confidence=0.9,
                reasoning="Always save notes",
                requires_confirmation=False
            )

        return None


class XcodeStrategy(BaseAppStrategy):
    """Strategy for Xcode"""

    def __init__(self):
        super().__init__("Xcode")

    def can_handle(self, context: Dict[str, Any]) -> bool:
        return context.get("app_name") == "Xcode"

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """Decide on Xcode dialogs"""
        question = context.get("question", "").lower()

        # Build errors/warnings
        if "build" in question:
            return StrategyDecision(
                chosen_option="Continue",
                confidence=0.5,
                reasoning="Allow continuing despite build warnings",
                requires_confirmation=True
            )

        # Delete derived data
        if "delete" in question and "derived" in question:
            return StrategyDecision(
                chosen_option="Delete",
                confidence=0.8,
                reasoning="Safe to delete derived data",
                requires_confirmation=False
            )

        # Code signing
        if "sign" in question or "certificate" in question:
            return StrategyDecision(
                chosen_option="Cancel",
                confidence=0.9,
                reasoning="Code signing requires user attention",
                requires_confirmation=True
            )

        return None


class PhotosStrategy(BaseAppStrategy):
    """Strategy for Photos.app"""

    def __init__(self):
        super().__init__("Photos")

    def can_handle(self, context: Dict[str, Any]) -> bool:
        return context.get("app_name") == "Photos"

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """Decide on Photos dialogs"""
        question = context.get("question", "").lower()

        # Delete photos confirmation
        if "delete" in question:
            return StrategyDecision(
                chosen_option="Delete",
                confidence=0.6,
                reasoning="Allow deleting photos (recoverable from Recently Deleted for 30 days)",
                requires_confirmation=False
            )

        # Import photos
        if "import" in question:
            return StrategyDecision(
                chosen_option="Import",
                confidence=0.8,
                reasoning="Auto-import photos",
                requires_confirmation=False
            )

        # Optimize storage
        if "optimize" in question or "storage" in question:
            return StrategyDecision(
                chosen_option="Optimize",
                confidence=0.7,
                reasoning="Allow storage optimization",
                requires_confirmation=False
            )

        return None


class SlackStrategy(BaseAppStrategy):
    """Strategy for Slack"""

    def __init__(self):
        super().__init__("Slack")

    def can_handle(self, context: Dict[str, Any]) -> bool:
        return context.get("app_name") == "Slack"

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """Decide on Slack dialogs"""
        question = context.get("question", "").lower()

        # Notification permissions
        if "notification" in question:
            return StrategyDecision(
                chosen_option="Allow",
                confidence=0.9,
                reasoning="Allow Slack notifications",
                requires_confirmation=False
            )

        # Update available
        if "update" in question:
            return StrategyDecision(
                chosen_option="Later",
                confidence=0.7,
                reasoning="Defer Slack updates to avoid interruption",
                requires_confirmation=False
            )

        return None


class AppStrategyManager:
    """
    Manager for application-specific strategies

    This class dispatches dialogs to the appropriate strategy based on
    the application name and dialog context.
    """

    def __init__(self):
        self.strategies = [
            TextEditStrategy(),
            FinderStrategy(),
            SafariStrategy(),
            MailStrategy(),
            NotesStrategy(),
            XcodeStrategy(),
            PhotosStrategy(),
            SlackStrategy(),
        ]

        logger.info(f"Initialized {len(self.strategies)} application strategies")

    def get_strategy(self, app_name: str) -> Optional[BaseAppStrategy]:
        """
        Get the strategy for a specific application

        Args:
            app_name: Name of the application

        Returns:
            Strategy instance or None if no strategy exists
        """
        for strategy in self.strategies:
            if strategy.app_name == app_name:
                return strategy
        return None

    def decide(self, context: Dict[str, Any]) -> Optional[StrategyDecision]:
        """
        Make a decision using application-specific strategy

        Args:
            context: Dialog context

        Returns:
            StrategyDecision or None if no strategy can handle it
        """
        app_name = context.get("app_name")

        # Try to find matching strategy
        for strategy in self.strategies:
            if strategy.can_handle(context):
                logger.debug(f"Using {strategy.__class__.__name__} for {app_name}")
                decision = strategy.decide(context)

                if decision:
                    logger.info(
                        f"Strategy decision for {app_name}: "
                        f"{decision.chosen_option} (confidence: {decision.confidence:.2f})"
                    )
                    return decision

        logger.debug(f"No specific strategy found for {app_name}")
        return None

    def register_strategy(self, strategy: BaseAppStrategy):
        """
        Register a new application strategy

        Args:
            strategy: Strategy instance to register
        """
        self.strategies.append(strategy)
        logger.info(f"Registered new strategy: {strategy.__class__.__name__}")


# Global strategy manager instance
strategy_manager = AppStrategyManager()
