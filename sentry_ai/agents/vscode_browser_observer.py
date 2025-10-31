"""
VS Code Browser Observer using Manus Browser API.

This module implements a VS Code observer that uses Manus Browser API
to detect and interact with Claude Code dialogs in VS Code's web interface.
"""

import re
import time
from typing import Optional, List, Callable
from loguru import logger

from ..models.data_models import DialogContext, UIElement


class VSCodeBrowserObserver:
    """
    VS Code Browser Observer using Manus Browser API.
    
    This observer uses Manus Browser API to detect Claude Code dialogs
    in VS Code's web interface. It's more reliable than Accessibility API
    for web-based VS Code instances.
    """
    
    def __init__(self):
        """Initialize the VS Code Browser Observer."""
        self.last_dialog_hash = None
        self.vscode_urls = [
            "vscode.dev",
            "github.dev",
            "localhost:3000",  # Local VS Code web
        ]
        logger.info("VS Code Browser Observer initialized")
    
    def is_vscode_page_open(self) -> bool:
        """
        Check if a VS Code page is currently open in the browser.
        
        Returns:
            True if VS Code page is open, False otherwise
        """
        try:
            # Note: This is a placeholder. In real implementation,
            # we would use browser_view() to check the current URL
            # For now, we'll assume it's available
            logger.debug("Checking if VS Code page is open")
            return True
        except Exception as e:
            logger.error(f"Error checking VS Code page: {e}")
            return False
    
    def detect_claude_dialog(self) -> Optional[DialogContext]:
        """
        Detect Claude Code dialogs in VS Code web interface.
        
        Uses Manus Browser API to:
        1. Get the current page content
        2. Look for Claude dialog patterns
        3. Extract buttons and options
        
        Returns:
            DialogContext if a dialog is detected, None otherwise
        """
        try:
            # Note: In real implementation, we would use browser_view()
            # For now, this is a template showing how it would work
            
            logger.debug("Detecting Claude dialog in browser")
            
            # This would be replaced with actual browser_view() call
            page_content = self._get_page_content()
            
            if not page_content:
                return None
            
            # Look for Claude dialog patterns
            dialog = self._parse_claude_dialog(page_content)
            
            if dialog:
                # Check for duplicates
                dialog_hash = self._hash_dialog(dialog)
                if dialog_hash == self.last_dialog_hash:
                    logger.debug("Duplicate dialog detected, skipping")
                    return None
                
                self.last_dialog_hash = dialog_hash
                logger.info(f"Claude dialog detected: {dialog.question[:50]}...")
                return dialog
            
            return None
        
        except Exception as e:
            logger.error(f"Error detecting Claude dialog: {e}")
            return None
    
    def _get_page_content(self) -> Optional[str]:
        """
        Get the current page content using Manus Browser API.
        
        In real implementation, this would use browser_view() to get
        the page content, including visible text and interactive elements.
        
        Returns:
            Page content as string, or None if not available
        """
        # Placeholder for actual browser_view() implementation
        # In production, this would be:
        # from manus import browser
        # result = browser.view()
        # return result['markdown_content']
        
        logger.debug("Getting page content (placeholder)")
        return None
    
    def _parse_claude_dialog(self, page_content: str) -> Optional[DialogContext]:
        """
        Parse Claude dialog from page content.
        
        Args:
            page_content: The page content from browser_view()
            
        Returns:
            DialogContext if a dialog is found, None otherwise
        """
        if not page_content:
            return None
        
        # Pattern 1: Bash command dialog
        bash_pattern = r"Allow this bash command\?\s*\n\s*\$\s*(.+)"
        bash_match = re.search(bash_pattern, page_content)
        
        if bash_match:
            command = bash_match.group(1).strip()
            return DialogContext(
                app_name="Visual Studio Code (Browser)",
                question=f"Allow this bash command?\n\n$ {command}",
                options=["Yes", "Yes, and don't ask again", "No", "Tell Claude what to do instead"],
                elements=[]  # Would be populated from browser elements
            )
        
        # Pattern 2: Edit automatically dialog
        if "Edit automatically" in page_content:
            return DialogContext(
                app_name="Visual Studio Code (Browser)",
                question="Edit automatically?",
                options=["Yes", "No"],
                elements=[]
            )
        
        # Pattern 3: Claude question (ends with ?)
        question_pattern = r"Claude:\s*(.+\?)"
        question_match = re.search(question_pattern, page_content)
        
        if question_match:
            question = question_match.group(1).strip()
            return DialogContext(
                app_name="Visual Studio Code (Browser)",
                question=question,
                options=[],  # No predefined options, needs text input
                elements=[]
            )
        
        return None
    
    def _hash_dialog(self, dialog: DialogContext) -> str:
        """
        Create a hash of the dialog to detect duplicates.
        
        Args:
            dialog: The dialog to hash
            
        Returns:
            Hash string
        """
        import hashlib
        content = f"{dialog.question}{''.join(dialog.options or [])}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def watch(
        self,
        callback: Callable[[DialogContext], None],
        interval: float = 1.0,
        duration: Optional[float] = None
    ):
        """
        Watch for Claude dialogs continuously.
        
        Args:
            callback: Function to call when a dialog is detected
            interval: Check interval in seconds
            duration: How long to watch (None = forever)
        """
        logger.info(f"Starting VS Code Browser watch (interval={interval}s)")
        
        start_time = time.time()
        
        try:
            while True:
                # Check if VS Code page is open
                if not self.is_vscode_page_open():
                    logger.debug("VS Code page not open, waiting...")
                    time.sleep(interval)
                    continue
                
                # Detect dialog
                dialog = self.detect_claude_dialog()
                
                if dialog:
                    callback(dialog)
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    logger.info("Watch duration reached, stopping")
                    break
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("Watch stopped by user")
        except Exception as e:
            logger.error(f"Error in watch loop: {e}")
    
    def get_button_elements(self) -> List[UIElement]:
        """
        Get button elements from the current page.
        
        Uses Manus Browser API to extract interactive elements.
        
        Returns:
            List of UIElement objects representing buttons
        """
        # Placeholder for actual browser element extraction
        # In production, this would parse the elements from browser_view()
        
        logger.debug("Getting button elements (placeholder)")
        return []


# Integration helper functions

def create_browser_observer() -> VSCodeBrowserObserver:
    """
    Create a VS Code Browser Observer instance.
    
    Returns:
        Configured VSCodeBrowserObserver
    """
    return VSCodeBrowserObserver()


def is_browser_available() -> bool:
    """
    Check if Manus Browser API is available.
    
    Returns:
        True if browser API is available, False otherwise
    """
    try:
        # In production, this would check if browser tools are available
        # For now, we assume they are
        return True
    except Exception as e:
        logger.error(f"Browser API not available: {e}")
        return False
