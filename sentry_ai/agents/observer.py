"""
Observer Agent for Sentry-AI.

This module implements the Observer agent that monitors the macOS UI
using the Accessibility API to detect dialogs and UI changes.
"""

import time
from typing import List, Optional, Callable
from loguru import logger

try:
    from AppKit import NSWorkspace
    from ApplicationServices import (
        AXUIElementCreateApplication,
        AXUIElementCopyAttributeValue,
        kAXWindowsAttribute,
        kAXChildrenAttribute,
        kAXRoleAttribute,
        kAXTitleAttribute,
        kAXValueAttribute,
    )
    MACOS_AVAILABLE = True
except ImportError:
    logger.warning("macOS frameworks not available. Observer will run in mock mode.")
    MACOS_AVAILABLE = False

from ..models.data_models import UIElement, ObserverEvent
from ..core.config import settings, is_app_allowed


class Observer:
    """
    Observer agent that monitors the macOS UI for dialogs and events.
    
    The Observer uses the macOS Accessibility API to detect when new windows
    or dialogs appear, and extracts their UI element hierarchy.
    """
    
    def __init__(self, callback: Optional[Callable[[ObserverEvent], None]] = None):
        """
        Initialize the Observer.
        
        Args:
            callback: Optional callback function to be called when an event is detected
        """
        self.callback = callback
        self.is_running = False
        self.last_checked_app = None
        
        if not MACOS_AVAILABLE:
            logger.warning("Running in mock mode - no actual UI monitoring will occur")
    
    def start(self):
        """Start the observer loop."""
        self.is_running = True
        logger.info("Observer started")
        logger.info(f"Blacklisted apps: {settings.blacklist_apps}")
        
        while self.is_running:
            try:
                self._check_for_dialogs()
                time.sleep(settings.observer_interval)
            except KeyboardInterrupt:
                logger.info("Observer stopped by user")
                self.stop()
            except Exception as e:
                logger.error(f"Error in observer loop: {e}")
                time.sleep(settings.observer_interval)
    
    def stop(self):
        """Stop the observer loop."""
        self.is_running = False
        logger.info("Observer stopped")
    
    def _check_for_dialogs(self):
        """Check the active application for dialogs."""
        if not MACOS_AVAILABLE:
            return
        
        try:
            # Get the active application
            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            app_name = active_app.get('NSApplicationName', 'Unknown')
            pid = active_app.get('NSApplicationProcessIdentifier')
            
            # Check if this app is allowed
            if not is_app_allowed(app_name):
                return
            
            # Get UI elements from the active window
            elements = self._get_window_elements(pid)
            
            if elements and self._is_dialog(elements):
                # Create and emit event
                event = ObserverEvent(
                    event_type="dialog_detected",
                    app_name=app_name,
                    elements=elements
                )
                
                logger.info(f"Dialog detected in {app_name}")
                
                if self.callback:
                    self.callback(event)
        
        except Exception as e:
            logger.debug(f"Error checking for dialogs: {e}")
    
    def _get_window_elements(self, pid: int) -> List[UIElement]:
        """
        Get UI elements from the active window of an application.
        
        Args:
            pid: Process ID of the application
            
        Returns:
            List of UIElement objects
        """
        if not MACOS_AVAILABLE:
            return []
        
        try:
            # Create application reference
            app_ref = AXUIElementCreateApplication(pid)
            
            # Get windows
            result, windows = AXUIElementCopyAttributeValue(
                app_ref, kAXWindowsAttribute, None
            )
            
            if result != 0 or not windows:
                return []
            
            # Get elements from the first (active) window
            active_window = windows[0]
            result, children = AXUIElementCopyAttributeValue(
                active_window, kAXChildrenAttribute, None
            )
            
            if result != 0 or not children:
                return []
            
            # Convert to UIElement objects
            elements = []
            for child in children:
                element = self._extract_element_info(child)
                if element:
                    elements.append(element)
            
            return elements
        
        except Exception as e:
            logger.debug(f"Error getting window elements: {e}")
            return []
    
    def _extract_element_info(self, ax_element) -> Optional[UIElement]:
        """
        Extract information from an AXUIElement.
        
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
    
    def _is_dialog(self, elements: List[UIElement]) -> bool:
        """
        Determine if the given elements represent a dialog.
        
        A dialog typically has:
        - At least one button
        - Some text content
        - Binary or multiple choice options
        
        Args:
            elements: List of UI elements to analyze
            
        Returns:
            True if this appears to be a dialog, False otherwise
        """
        buttons = [e for e in elements if e.role == "AXButton"]
        texts = [e for e in elements if e.role in ["AXStaticText", "AXTextField"]]
        
        # Simple heuristic: at least 2 buttons and some text
        return len(buttons) >= 2 and len(texts) >= 1
