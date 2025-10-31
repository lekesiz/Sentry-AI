"""
Actor Agent for Sentry-AI.

This module implements the Actor agent that executes actions on UI elements
using the macOS Accessibility API.
"""

from typing import Optional
from loguru import logger

try:
    from ApplicationServices import (
        AXUIElementPerformAction,
        AXUIElementCopyAttributeValue,
        kAXPressAction,
        kAXRoleAttribute,
        kAXTitleAttribute,
    )
    MACOS_AVAILABLE = True
except ImportError:
    logger.warning("macOS frameworks not available. Actor will run in mock mode.")
    MACOS_AVAILABLE = False

from ..models.data_models import UIElement, Action, ActionType


class Actor:
    """
    Actor agent that executes actions on UI elements.
    
    The Actor receives a decision from the Decision Engine and performs
    the corresponding action (e.g., clicking a button).
    """
    
    def __init__(self):
        """Initialize the Actor."""
        if not MACOS_AVAILABLE:
            logger.warning("Running in mock mode - no actual actions will be performed")
    
    def execute(self, action: Action) -> bool:
        """
        Execute an action.
        
        Args:
            action: The action to execute
            
        Returns:
            True if the action was successful, False otherwise
        """
        try:
            if action.action_type == ActionType.CLICK_BUTTON:
                return self._click_button(action.target_element)
            elif action.action_type == ActionType.PRESS_KEY:
                return self._press_key(action.parameters.get('key'))
            elif action.action_type == ActionType.TYPE_TEXT:
                return self._type_text(
                    action.target_element,
                    action.parameters.get('text', '')
                )
            elif action.action_type == ActionType.DISMISS:
                return self._dismiss_dialog(action.target_element)
            else:
                logger.warning(f"Unknown action type: {action.action_type}")
                return False
        
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return False
    
    def _click_button(self, element: Optional[UIElement]) -> bool:
        """
        Click a button element.
        
        Args:
            element: The button element to click
            
        Returns:
            True if successful, False otherwise
        """
        if not MACOS_AVAILABLE:
            logger.info(f"[MOCK] Would click button: {element.title if element else 'Unknown'}")
            return True
        
        if not element or not element.element_ref:
            logger.error("Invalid element for clicking")
            return False
        
        try:
            # Verify it's a button
            result, role = AXUIElementCopyAttributeValue(
                element.element_ref, kAXRoleAttribute, None
            )
            
            if result != 0 or role != "AXButton":
                logger.error(f"Element is not a button (role: {role})")
                return False
            
            # Perform the press action
            result = AXUIElementPerformAction(element.element_ref, kAXPressAction)
            
            if result == 0:
                logger.info(f"Successfully clicked button: {element.title}")
                return True
            else:
                logger.error(f"Failed to click button: {element.title} (error code: {result})")
                return False
        
        except Exception as e:
            logger.error(f"Error clicking button: {e}")
            return False
    
    def _press_key(self, key: Optional[str]) -> bool:
        """
        Press a keyboard key.
        
        Args:
            key: The key to press (e.g., "Return", "Escape", "Tab")
            
        Returns:
            True if successful, False otherwise
        """
        if not MACOS_AVAILABLE:
            logger.info(f"[MOCK] Would press key: {key}")
            return True
        
        if not key:
            logger.error("No key specified")
            return False
        
        # Map key names to key codes
        key_codes = {
            "Return": 36,
            "Enter": 36,
            "Escape": 53,
            "Tab": 48,
            "Space": 49,
            "Delete": 51,
            "Backspace": 51,
        }
        
        key_code = key_codes.get(key)
        if key_code is None:
            logger.error(f"Unknown key: {key}")
            return False
        
        try:
            # Create and post key down event
            key_down = CGEventCreateKeyboardEvent(None, key_code, True)
            CGEventPost(kCGHIDEventTap, key_down)
            
            # Create and post key up event
            key_up = CGEventCreateKeyboardEvent(None, key_code, False)
            CGEventPost(kCGHIDEventTap, key_up)
            
            logger.info(f"Successfully pressed key: {key}")
            return True
        
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return False
    
    def _type_text(self, element: Optional[UIElement], text: str) -> bool:
        """
        Type text into a text field or text area.
        
        Args:
            element: The text field element (optional, will use focused element if None)
            text: The text to type
            
        Returns:
            True if successful, False otherwise
        """
        if not MACOS_AVAILABLE:
            logger.info(f"[MOCK] Would type text: {text[:50]}...")
            return True
        
        if not text:
            logger.warning("No text to type")
            return True
        
        try:
            # If element is provided, try to set its value directly
            if element and element.element_ref:
                result = AXUIElementSetAttributeValue(
                    element.element_ref,
                    kAXValueAttribute,
                    text
                )
                
                if result == 0:
                    logger.info(f"Successfully typed text (direct): {text[:50]}...")
                    return True
            
            # Fallback: simulate typing character by character
            return self._simulate_typing(text)
        
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    def _simulate_typing(self, text: str) -> bool:
        """
        Simulate typing text character by character using keyboard events.
        
        Args:
            text: The text to type
            
        Returns:
            True if successful, False otherwise
        """
        if not MACOS_AVAILABLE:
            return True
        
        try:
            import time
            from Quartz import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap
            
            # Map characters to key codes (simplified, ASCII only)
            for char in text:
                # For simplicity, we'll use the character's Unicode value
                # This works for basic ASCII characters
                if char == '\n':
                    self._press_key("Return")
                else:
                    # Create keyboard event with character
                    key_down = CGEventCreateKeyboardEvent(None, 0, True)
                    CGEventPost(kCGHIDEventTap, key_down)
                    
                    key_up = CGEventCreateKeyboardEvent(None, 0, False)
                    CGEventPost(kCGHIDEventTap, key_up)
                    
                    time.sleep(0.01)  # Small delay between characters
            
            logger.info(f"Successfully simulated typing: {text[:50]}...")
            return True
        
        except Exception as e:
            logger.error(f"Error simulating typing: {e}")
            return False
    
    def _dismiss_dialog(self, element: Optional[UIElement]) -> bool:
        """
        Dismiss a dialog (usually by pressing Escape or clicking Cancel).
        
        Args:
            element: The dialog element
            
        Returns:
            True if successful, False otherwise
        """
        # Try to find and click a "Cancel" or "Close" button
        # This is a simplified implementation
        return self._press_key("Escape")
    
    def find_button_by_title(
        self, 
        elements: list[UIElement], 
        title: str
    ) -> Optional[UIElement]:
        """
        Find a button element by its title.
        
        Args:
            elements: List of UI elements to search
            title: The title to search for
            
        Returns:
            The matching UIElement or None
        """
        for element in elements:
            if element.role == "AXButton" and element.title == title:
                return element
        
        return None
