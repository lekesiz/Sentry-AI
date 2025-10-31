"""
Analyzer Agent for Sentry-AI.

This module implements the Analyzer agent that extracts context from
detected dialogs and prepares it for the Decision Engine.
"""

from typing import List, Optional
from loguru import logger

from ..models.data_models import UIElement, DialogContext, DialogType


class Analyzer:
    """
    Analyzer agent that extracts context from UI elements.
    
    The Analyzer takes the raw UI elements from the Observer and constructs
    a structured DialogContext that can be used by the Decision Engine.
    """
    
    def __init__(self):
        """Initialize the Analyzer."""
        self.dialog_keywords = {
            DialogType.SAVE_CONFIRMATION: [
                "save", "enregistrer", "kaydet", "guardar",
                "don't save", "ne pas enregistrer", "kaydetme"
            ],
            DialogType.UPDATE_PROMPT: [
                "update", "mise à jour", "güncelleme", "actualizar"
            ],
            DialogType.PERMISSION_REQUEST: [
                "allow", "autoriser", "izin ver", "permitir",
                "deny", "refuser", "reddet", "denegar"
            ],
            DialogType.ERROR_DIALOG: [
                "error", "erreur", "hata", "failed", "échec"
            ]
        }
    
    def analyze(self, app_name: str, elements: List[UIElement]) -> Optional[DialogContext]:
        """
        Analyze UI elements and extract dialog context.
        
        Args:
            app_name: Name of the application
            elements: List of UI elements from the Observer
            
        Returns:
            DialogContext object or None if analysis fails
        """
        try:
            # Extract buttons
            buttons = [e for e in elements if e.role == "AXButton" and e.title]
            button_labels = [b.title for b in buttons]
            
            if not button_labels:
                logger.debug("No buttons found in dialog")
                return None
            
            # Extract text content
            texts = [
                e for e in elements 
                if e.role in ["AXStaticText", "AXTextField"] and e.value
            ]
            question = " ".join([str(t.value) for t in texts])
            
            if not question:
                logger.debug("No text content found in dialog")
                return None
            
            # Determine dialog type
            dialog_type = self._classify_dialog_type(question, button_labels)
            
            # Get window title if available
            window_title = self._extract_window_title(elements)
            
            context = DialogContext(
                app_name=app_name,
                window_title=window_title,
                dialog_type=dialog_type,
                question=question,
                options=button_labels,
                elements=elements
            )
            
            logger.info(
                f"Analyzed dialog: {dialog_type.value} in {app_name} "
                f"with options: {button_labels}"
            )
            
            return context
        
        except Exception as e:
            logger.error(f"Error analyzing dialog: {e}")
            return None
    
    def _classify_dialog_type(
        self, 
        question: str, 
        button_labels: List[str]
    ) -> DialogType:
        """
        Classify the type of dialog based on content.
        
        Args:
            question: The dialog question/message
            button_labels: List of button labels
            
        Returns:
            DialogType enum value
        """
        combined_text = (question + " " + " ".join(button_labels)).lower()
        
        for dialog_type, keywords in self.dialog_keywords.items():
            if any(keyword.lower() in combined_text for keyword in keywords):
                return dialog_type
        
        return DialogType.GENERIC
    
    def _extract_window_title(self, elements: List[UIElement]) -> Optional[str]:
        """
        Extract the window title from elements.
        
        Args:
            elements: List of UI elements
            
        Returns:
            Window title or None
        """
        # Look for an element with role AXWindow or AXDialog
        for element in elements:
            if element.role in ["AXWindow", "AXDialog"] and element.title:
                return element.title
        
        return None
    
    def analyze_with_ocr(
        self, 
        app_name: str, 
        screenshot_path: str
    ) -> Optional[DialogContext]:
        """
        Analyze a dialog using OCR as a fallback method.
        
        This method is used when the Accessibility API doesn't provide
        sufficient information (e.g., for non-native apps).
        
        Args:
            app_name: Name of the application
            screenshot_path: Path to the screenshot to analyze
            
        Returns:
            DialogContext object or None if analysis fails
        """
        # TODO: Implement OCR using Apple Vision Framework
        logger.warning("OCR analysis not yet implemented")
        return None
