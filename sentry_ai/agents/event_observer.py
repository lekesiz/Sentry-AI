"""
Event-Driven Observer Agent for Sentry-AI.

This module implements an event-driven observer that uses macOS
Distributed Notifications and NSWorkspace notifications instead of polling.
"""

import threading
from typing import Optional, Callable
from loguru import logger

try:
    from AppKit import (
        NSWorkspace,
        NSNotificationCenter,
        NSDistributedNotificationCenter,
    )
    from Foundation import NSObject
    from ApplicationServices import (
        AXUIElementCreateApplication,
        AXUIElementCopyAttributeValue,
        AXObserverCreate,
        AXObserverAddNotification,
        kAXWindowsAttribute,
        kAXChildrenAttribute,
        kAXRoleAttribute,
        kAXTitleAttribute,
        kAXValueAttribute,
        kAXCreatedNotification,
        kAXFocusedWindowChangedNotification,
        kAXWindowCreatedNotification,
    )
    import Quartz
    MACOS_AVAILABLE = True
except ImportError:
    logger.warning("macOS frameworks not available. Event observer will run in mock mode.")
    MACOS_AVAILABLE = False

from ..models.data_models import UIElement, ObserverEvent
from ..core.config import settings, is_app_allowed


class NotificationHandler(NSObject):
    """Handler for macOS notifications"""

    def initWithCallback_(self, callback):
        """Initialize with callback function"""
        self = NSObject.init(self)
        if self is None:
            return None
        self.callback = callback
        return self

    def handleNotification_(self, notification):
        """Handle incoming notification"""
        try:
            if self.callback:
                self.callback(notification)
        except Exception as e:
            logger.error(f"Error in notification handler: {e}")


class EventDrivenObserver:
    """
    Event-driven observer that monitors macOS UI using notifications.

    Instead of polling every N seconds, this observer:
    1. Subscribes to NSWorkspace notifications for app activation
    2. Subscribes to AXObserver notifications for window creation
    3. Responds only when actual UI changes occur

    Benefits:
    - Near-zero CPU usage when idle
    - Instant response to UI changes
    - More battery efficient
    - Scalable to many applications
    """

    def __init__(self, callback: Optional[Callable[[ObserverEvent], None]] = None):
        """
        Initialize the Event-Driven Observer.

        Args:
            callback: Optional callback function to be called when an event is detected
        """
        self.callback = callback
        self.is_running = False
        self.workspace = None
        self.notification_center = None
        self.app_observers = {}  # pid -> AXObserver mapping
        self.handler = None

        if not MACOS_AVAILABLE:
            logger.warning("Running in mock mode - no actual UI monitoring will occur")

    def start(self):
        """Start the event-driven observer"""
        if not MACOS_AVAILABLE:
            logger.error("Cannot start observer - macOS frameworks not available")
            return

        self.is_running = True
        logger.info("Event-Driven Observer starting...")
        logger.info(f"Blacklisted apps: {settings.blacklist_apps}")

        # Get shared workspace
        self.workspace = NSWorkspace.sharedWorkspace()
        self.notification_center = self.workspace.notificationCenter()

        # Create notification handler
        self.handler = NotificationHandler.alloc().initWithCallback_(
            self._on_app_activation
        )

        # Subscribe to app activation notifications
        self.notification_center.addObserver_selector_name_object_(
            self.handler,
            "handleNotification:",
            "NSWorkspaceDidActivateApplicationNotification",
            None
        )

        logger.success("✅ Event-Driven Observer started successfully")
        logger.info("📡 Listening for application activation events...")
        logger.info("⚡ CPU usage: ~0% when idle (event-driven mode)")

        # Start monitoring currently active app
        active_app = self.workspace.activeApplication()
        if active_app:
            self._setup_app_observer(active_app)

        # Keep the observer running
        self._run_event_loop()

    def stop(self):
        """Stop the event-driven observer"""
        self.is_running = False

        # Remove all app observers
        for pid, observer in self.app_observers.items():
            logger.debug(f"Removing observer for PID {pid}")
            # AX observers are automatically cleaned up

        self.app_observers.clear()

        # Remove notification center observer
        if self.notification_center and self.handler:
            self.notification_center.removeObserver_(self.handler)

        logger.info("Event-Driven Observer stopped")

    def _run_event_loop(self):
        """Run the event loop to keep the observer alive"""
        from Foundation import NSRunLoop, NSDefaultRunLoopMode, NSDate

        logger.info("Starting event loop...")

        # Run the run loop
        while self.is_running:
            try:
                # Run loop for a short interval
                NSRunLoop.currentRunLoop().runMode_beforeDate_(
                    NSDefaultRunLoopMode,
                    NSDate.dateWithTimeIntervalSinceNow_(0.5)
                )
            except KeyboardInterrupt:
                logger.info("Observer stopped by user")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in event loop: {e}")

    def _on_app_activation(self, notification):
        """
        Called when an application is activated

        Args:
            notification: NSNotification object
        """
        try:
            user_info = notification.userInfo()
            app = user_info.get("NSWorkspaceApplicationKey")

            if not app:
                return

            app_name = app.localizedName()
            pid = app.processIdentifier()

            logger.debug(f"App activated: {app_name} (PID: {pid})")

            # Check if this app is allowed
            if not is_app_allowed(app_name):
                logger.debug(f"App {app_name} is blacklisted, ignoring")
                return

            # Setup AX observer for this app
            self._setup_app_observer(app)

        except Exception as e:
            logger.error(f"Error handling app activation: {e}")

    def _setup_app_observer(self, app):
        """
        Setup Accessibility API observer for an application

        Args:
            app: NSRunningApplication object
        """
        try:
            pid = app.processIdentifier()
            app_name = app.localizedName()

            # Skip if we already have an observer for this app
            if pid in self.app_observers:
                return

            logger.debug(f"Setting up AX observer for {app_name} (PID: {pid})")

            # Create AX observer
            def ax_callback(observer, element, notification_name, refcon):
                """Callback for AX notifications"""
                try:
                    self._on_window_event(app_name, pid, element, notification_name)
                except Exception as e:
                    logger.error(f"Error in AX callback: {e}")

            # Create application reference
            app_ref = AXUIElementCreateApplication(pid)

            # Create observer
            result, observer = AXObserverCreate(pid, ax_callback, None)

            if result != 0:
                logger.debug(f"Failed to create observer for {app_name}: error {result}")
                return

            # Add notifications to observe
            notifications = [
                kAXWindowCreatedNotification,
                kAXFocusedWindowChangedNotification,
            ]

            for notif in notifications:
                result = AXObserverAddNotification(
                    observer,
                    app_ref,
                    notif,
                    None
                )

                if result == 0:
                    logger.debug(f"✅ Subscribed to {notif} for {app_name}")
                else:
                    logger.debug(f"⚠️  Failed to subscribe to {notif}: error {result}")

            # Add observer to run loop
            from Foundation import CFRunLoopGetCurrent, kCFRunLoopDefaultMode
            from ApplicationServices import AXObserverGetRunLoopSource, CFRunLoopAddSource

            run_loop_source = AXObserverGetRunLoopSource(observer)
            CFRunLoopAddSource(
                CFRunLoopGetCurrent(),
                run_loop_source,
                kCFRunLoopDefaultMode
            )

            # Store observer
            self.app_observers[pid] = observer

            logger.success(f"✅ AX observer setup complete for {app_name}")

        except Exception as e:
            logger.error(f"Error setting up app observer: {e}")

    def _on_window_event(self, app_name: str, pid: int, element, notification_name: str):
        """
        Called when a window event occurs

        Args:
            app_name: Name of the application
            pid: Process ID
            element: AXUIElement that triggered the event
            notification_name: Name of the notification
        """
        try:
            logger.debug(f"Window event: {notification_name} in {app_name}")

            # Get UI elements from the window
            elements = self._get_element_hierarchy(element)

            if elements and self._is_dialog(elements):
                # Create and emit event
                event = ObserverEvent(
                    event_type="dialog_detected",
                    app_name=app_name,
                    elements=elements
                )

                logger.info(f"⚡ Dialog detected in {app_name} (event-driven)")

                if self.callback:
                    # Run callback in a separate thread to avoid blocking
                    thread = threading.Thread(
                        target=self.callback,
                        args=(event,),
                        daemon=True
                    )
                    thread.start()

        except Exception as e:
            logger.error(f"Error handling window event: {e}")

    def _get_element_hierarchy(self, element) -> list:
        """
        Get the UI element hierarchy from an AXUIElement

        Args:
            element: The AXUIElement to extract hierarchy from

        Returns:
            List of UIElement objects
        """
        try:
            elements = []

            # Get children
            result, children = AXUIElementCopyAttributeValue(
                element, kAXChildrenAttribute, None
            )

            if result != 0 or not children:
                # Try to extract just this element
                elem = self._extract_element_info(element)
                if elem:
                    return [elem]
                return []

            # Extract each child
            for child in children:
                elem = self._extract_element_info(child)
                if elem:
                    elements.append(elem)

                # Recursively get children of children (limited depth)
                result, grandchildren = AXUIElementCopyAttributeValue(
                    child, kAXChildrenAttribute, None
                )
                if result == 0 and grandchildren:
                    for grandchild in grandchildren[:10]:  # Limit depth
                        gc_elem = self._extract_element_info(grandchild)
                        if gc_elem:
                            elements.append(gc_elem)

            return elements

        except Exception as e:
            logger.debug(f"Error getting element hierarchy: {e}")
            return []

    def _extract_element_info(self, ax_element) -> Optional[UIElement]:
        """
        Extract information from an AXUIElement

        Args:
            ax_element: The AXUIElement to extract info from

        Returns:
            UIElement object or None if extraction fails
        """
        try:
            # Get role
            result, role = AXUIElementCopyAttributeValue(
                ax_element, kAXRoleAttribute, None
            )
            if result != 0:
                return None

            # Get title
            result, title = AXUIElementCopyAttributeValue(
                ax_element, kAXTitleAttribute, None
            )
            title = title if result == 0 else None

            # Get value
            result, value = AXUIElementCopyAttributeValue(
                ax_element, kAXValueAttribute, None
            )
            value = value if result == 0 else None

            return UIElement(
                role=role,
                title=title,
                value=value,
                element_ref=ax_element
            )

        except Exception as e:
            logger.debug(f"Error extracting element info: {e}")
            return None

    def _is_dialog(self, elements: list) -> bool:
        """
        Determine if the given elements represent a dialog

        Args:
            elements: List of UI elements to analyze

        Returns:
            True if this appears to be a dialog, False otherwise
        """
        buttons = [e for e in elements if e.role == "AXButton"]
        texts = [e for e in elements if e.role in ["AXStaticText", "AXTextField"]]

        # Simple heuristic: at least 2 buttons and some text
        return len(buttons) >= 2 and len(texts) >= 1
