"""
VS Code Observer for Sentry-AI.

This module implements a specialized Observer for Visual Studio Code,
specifically designed to detect and handle Claude Code extension dialogs.
"""

from typing import List, Optional, Dict
from loguru import logger
import time

try:
    from Foundation import NSWorkspace
    from AppKit import NSApplication, NSRunningApplication
    from ApplicationServices import (
        AXUIElementCreateApplication,
        AXUIElementCopyAttributeValue,
        AXUIElementCopyAttributeNames,
        kAXWindowsAttribute,
        kAXTitleAttribute,
        kAXChildrenAttribute,
        kAXRoleAttribute,
        kAXValueAttribute,
        kAXDescriptionAttribute,
        kAXButtonRole,
        kAXStaticTextRole,
        kAXTextFieldRole,
        kAXTextAreaRole,
    )
    MACOS_AVAILABLE = True
except ImportError:
    logger.warning("macOS frameworks not available. VS Code Observer will run in mock mode.")
    MACOS_AVAILABLE = False

from ..models.data_models import UIElement, DialogContext, DialogType


class VSCodeObserver:
    """
    Specialized Observer for Visual Studio Code.
    
    Detects Claude Code extension dialogs and extracts relevant information.
    """
    
    def __init__(self):
        """Initialize the VS Code Observer."""
        self.vscode_bundle_ids = [
            "com.microsoft.VSCode",
            "com.microsoft.VSCodeInsiders",
            "com.visualstudio.code.oss"
        ]
        self.last_dialog_hash = None
    
    def is_vscode_running(self) -> bool:
        """Check if VS Code is currently running."""
        if not MACOS_AVAILABLE:
            return False
        
        workspace = NSWorkspace.sharedWorkspace()
        running_apps = workspace.runningApplications()
        
        for app in running_apps:
            if app.bundleIdentifier() in self.vscode_bundle_ids:
                return True
        
        return False
    
    def get_vscode_app(self) -> Optional[any]:
        """Get the VS Code application reference."""
        if not MACOS_AVAILABLE:
            return None
        
        workspace = NSWorkspace.sharedWorkspace()
        running_apps = workspace.runningApplications()
        
        for app in running_apps:
            if app.bundleIdentifier() in self.vscode_bundle_ids:
                pid = app.processIdentifier()
                return AXUIElementCreateApplication(pid)
        
        return None
    
    def detect_claude_dialog(self) -> Optional[DialogContext]:
        """
        Detect Claude Code extension dialogs in VS Code.
        
        Returns:
            DialogContext if a dialog is detected, None otherwise
        """
        if not self.is_vscode_running():
            return None
        
        vscode_app = self.get_vscode_app()
        if not vscode_app:
            return None
        
        try:
            # Get all windows
            _, windows = AXUIElementCopyAttributeValue(vscode_app, kAXWindowsAttribute, None)
            
            if not windows:
                return None
            
            # Search for Claude dialog patterns
            for window in windows:
                dialog = self._analyze_window_for_claude_dialog(window)
                if dialog:
                    # Check if this is a new dialog (avoid duplicates)
                    dialog_hash = self._hash_dialog(dialog)
                    if dialog_hash != self.last_dialog_hash:
                        self.last_dialog_hash = dialog_hash
                        return dialog
            
            return None
        
        except Exception as e:
            logger.debug(f"Error detecting Claude dialog: {e}")
            return None
    
    def _analyze_window_for_claude_dialog(self, window) -> Optional[DialogContext]:
        """
        Analyze a window to detect Claude Code dialogs.
        
        Args:
            window: AXUIElement window reference
            
        Returns:
            DialogContext if Claude dialog detected, None otherwise
        """
        try:
            # Get window title
            _, window_title = AXUIElementCopyAttributeValue(window, kAXTitleAttribute, None)
            
            # Get all children elements
            _, children = AXUIElementCopyAttributeValue(window, kAXChildrenAttribute, None)
            
            if not children:
                return None
            
            # Extract all UI elements
            elements = []
            buttons = []
            text_content = []
            
            self._extract_elements_recursive(children, elements, buttons, text_content)
            
            # Check for Claude dialog patterns
            if self._is_claude_dialog(text_content, buttons):
                # Extract question/prompt
                question = self._extract_question(text_content)
                
                # Extract button options
                options = [btn.title for btn in buttons if btn.title]
                
                return DialogContext(
                    app_name="Visual Studio Code",
                    window_title=window_title or "VS Code",
                    dialog_type=DialogType.PERMISSION_REQUEST,
                    question=question,
                    options=options,
                    elements=elements
                )
            
            return None
        
        except Exception as e:
            logger.debug(f"Error analyzing window: {e}")
            return None
    
    def _extract_elements_recursive(
        self,
        children: List,
        elements: List[UIElement],
        buttons: List[UIElement],
        text_content: List[str]
    ):
        """
        Recursively extract UI elements from children.
        
        Args:
            children: List of child elements
            elements: Output list for all elements
            buttons: Output list for button elements
            text_content: Output list for text content
        """
        if not children:
            return
        
        for child in children:
            try:
                # Get element role
                _, role = AXUIElementCopyAttributeValue(child, kAXRoleAttribute, None)
                
                # Get element title/value
                _, title = AXUIElementCopyAttributeValue(child, kAXTitleAttribute, None)
                _, value = AXUIElementCopyAttributeValue(child, kAXValueAttribute, None)
                _, description = AXUIElementCopyAttributeValue(child, kAXDescriptionAttribute, None)
                
                # Create UIElement
                element = UIElement(
                    role=role or "Unknown",
                    title=title,
                    value=value,
                    element_ref=child
                )
                
                elements.append(element)
                
                # Collect buttons
                if role == kAXButtonRole and title:
                    buttons.append(element)
                
                # Collect text content
                if role in [kAXStaticTextRole, kAXTextFieldRole, kAXTextAreaRole]:
                    if title:
                        text_content.append(str(title))
                    if value:
                        text_content.append(str(value))
                
                # Recurse into children
                _, grandchildren = AXUIElementCopyAttributeValue(child, kAXChildrenAttribute, None)
                if grandchildren:
                    self._extract_elements_recursive(grandchildren, elements, buttons, text_content)
            
            except Exception as e:
                logger.debug(f"Error extracting element: {e}")
                continue
    
    def _is_claude_dialog(self, text_content: List[str], buttons: List[UIElement]) -> bool:
        """
        Check if this is a Claude Code dialog.
        
        Args:
            text_content: List of text content
            buttons: List of button elements
            
        Returns:
            True if this is a Claude dialog
        """
        # Claude dialog indicators
        claude_keywords = [
            "claude",
            "allow this bash command",
            "allow this command",
            "edit automatically",
            "tell claude what to do instead",
            "yes",
            "yes, and don't ask again",
            "no"
        ]
        
        # Check text content
        all_text = " ".join(text_content).lower()
        
        for keyword in claude_keywords:
            if keyword in all_text:
                return True
        
        # Check button labels
        button_labels = [btn.title.lower() for btn in buttons if btn.title]
        
        for label in button_labels:
            for keyword in claude_keywords:
                if keyword in label:
                    return True
        
        return False
    
    def _extract_question(self, text_content: List[str]) -> str:
        """
        Extract the main question/prompt from text content.
        
        Args:
            text_content: List of text content
            
        Returns:
            Extracted question
        """
        if not text_content:
            return "No question detected"
        
        # Filter out very short strings
        meaningful_text = [t for t in text_content if len(t) > 10]
        
        if not meaningful_text:
            return text_content[0] if text_content else "No question detected"
        
        # Return the longest text (usually the main question)
        return max(meaningful_text, key=len)
    
    def _hash_dialog(self, dialog: DialogContext) -> str:
        """
        Create a hash of the dialog to detect duplicates.
        
        Args:
            dialog: DialogContext
            
        Returns:
            Hash string
        """
        return f"{dialog.app_name}:{dialog.question}:{','.join(dialog.options or [])}"
    
    def watch(self, callback, interval: float = 1.0):
        """
        Continuously watch for Claude dialogs.
        
        Args:
            callback: Function to call when a dialog is detected
            interval: Polling interval in seconds
        """
        logger.info("VS Code Observer started")
        
        try:
            while True:
                dialog = self.detect_claude_dialog()
                if dialog:
                    logger.info(f"Claude dialog detected: {dialog.question}")
                    callback(dialog)
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("VS Code Observer stopped")
        except Exception as e:
            logger.error(f"VS Code Observer error: {e}")
