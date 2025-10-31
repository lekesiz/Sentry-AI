"""
Data models for Sentry-AI.

This module defines all the data structures used throughout the application
using Pydantic for validation and serialization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DialogType(str, Enum):
    """Types of dialogs that can be detected."""
    SAVE_CONFIRMATION = "save_confirmation"
    UPDATE_PROMPT = "update_prompt"
    PERMISSION_REQUEST = "permission_request"
    ERROR_DIALOG = "error_dialog"
    GENERIC = "generic"


class ActionType(str, Enum):
    """Types of actions that can be performed."""
    CLICK_BUTTON = "click_button"
    PRESS_KEY = "press_key"
    TYPE_TEXT = "type_text"
    DISMISS = "dismiss"
    WAIT = "wait"


class UIElement(BaseModel):
    """Represents a UI element detected by the Observer."""
    role: str = Field(..., description="Accessibility role (e.g., AXButton, AXStaticText)")
    title: Optional[str] = Field(None, description="Title or label of the element")
    value: Optional[Any] = Field(None, description="Value of the element")
    position: Optional[Dict[str, float]] = Field(None, description="Position on screen")
    element_ref: Optional[Any] = Field(None, description="Reference to the actual UI element")
    
    class Config:
        arbitrary_types_allowed = True


class DialogContext(BaseModel):
    """Context information about a detected dialog."""
    app_name: str = Field(..., description="Name of the application showing the dialog")
    window_title: Optional[str] = Field(None, description="Title of the window")
    dialog_type: DialogType = Field(DialogType.GENERIC, description="Type of dialog")
    
    # Support both old and new field names for compatibility
    question: Optional[str] = Field(None, description="The question or message shown to the user")
    dialog_title: Optional[str] = Field(None, description="Alias for window_title")
    dialog_text: Optional[str] = Field(None, description="Alias for question")
    
    options: Optional[List[str]] = Field(None, description="Available options (button labels)")
    available_options: Optional[List[str]] = Field(None, description="Alias for options")
    
    elements: List[UIElement] = Field(default_factory=list, description="All UI elements in the dialog")
    timestamp: datetime = Field(default_factory=datetime.now)
    screenshot_path: Optional[str] = Field(None, description="Path to screenshot if OCR was used")
    
    def __init__(self, **data):
        # Handle aliases
        if 'dialog_title' in data and 'window_title' not in data:
            data['window_title'] = data['dialog_title']
        if 'dialog_text' in data and 'question' not in data:
            data['question'] = data['dialog_text']
        if 'available_options' in data and 'options' not in data:
            data['options'] = data['available_options']
        super().__init__(**data)
    
    @property
    def get_options(self) -> List[str]:
        """Get options list (handles both field names)."""
        return self.options or self.available_options or []


class AIDecision(BaseModel):
    """Decision made by the AI engine."""
    chosen_option: str = Field(..., description="The option chosen by the AI")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: Optional[str] = Field(None, description="Explanation of the decision")
    requires_confirmation: bool = Field(False, description="Whether user confirmation is needed")


class Action(BaseModel):
    """An action to be performed by the Actor."""
    action_type: ActionType = Field(..., description="Type of action to perform")
    target_element: Optional[UIElement] = Field(None, description="Target UI element")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")


class ActionLog(BaseModel):
    """Log entry for an action performed by Sentry-AI."""
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    app_name: str
    dialog_context: DialogContext
    ai_decision: AIDecision
    action_performed: Action
    success: bool
    error_message: Optional[str] = None
    execution_time_ms: float
    
    class Config:
        from_attributes = True


class ObserverEvent(BaseModel):
    """Event emitted by the Observer when a dialog is detected."""
    event_type: str = Field(..., description="Type of event (e.g., 'dialog_detected')")
    app_name: str
    elements: List[UIElement]
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemStatus(BaseModel):
    """Current status of the Sentry-AI system."""
    is_running: bool
    observer_active: bool
    ollama_available: bool
    actions_performed_today: int
    last_action_timestamp: Optional[datetime] = None
    uptime_seconds: float
