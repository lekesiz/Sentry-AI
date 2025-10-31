"""
Decision Engine for Sentry-AI.

This module implements the Decision Engine that uses a local LLM (via Ollama)
to make intelligent decisions about how to respond to dialogs.
"""

from typing import Optional
from loguru import logger

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    logger.warning("Ollama package not available. Decision Engine will use fallback logic.")
    OLLAMA_AVAILABLE = False

from ..models.data_models import DialogContext, AIDecision
from ..core.config import settings, requires_confirmation


class DecisionEngine:
    """
    Decision Engine that uses AI to decide how to respond to dialogs.
    
    The engine sends context to a local LLM (via Ollama) and interprets
    the response to make an informed decision.
    """
    
    def __init__(self):
        """Initialize the Decision Engine."""
        self.ollama_available = self._check_ollama_availability()
        
        if not self.ollama_available:
            logger.warning("Ollama not available. Using rule-based fallback.")
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and the model is loaded."""
        if not OLLAMA_AVAILABLE:
            return False
        
        try:
            # Try to list models to verify connection
            ollama.list()
            logger.info(f"Ollama is available. Using model: {settings.ollama_model}")
            return True
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Make a decision about how to respond to a dialog.
        
        Args:
            context: The dialog context to analyze
            
        Returns:
            AIDecision object or None if decision cannot be made
        """
        try:
            if self.ollama_available:
                return self._decide_with_ai(context)
            else:
                return self._decide_with_rules(context)
        
        except Exception as e:
            logger.error(f"Error making decision: {e}")
            return None
    
    def _decide_with_ai(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Use the LLM to make a decision.
        
        Args:
            context: The dialog context
            
        Returns:
            AIDecision object or None
        """
        try:
            # Construct the prompt
            prompt = self._build_prompt(context)
            
            # Call Ollama
            response = ollama.chat(
                model=settings.ollama_model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': settings.ollama_temperature}
            )
            
            # Extract the decision
            ai_response = response['message']['content'].strip()
            
            # Find the matching option
            chosen_option = self._match_option(ai_response, context.options)
            
            if not chosen_option:
                logger.warning(f"AI response '{ai_response}' doesn't match any option")
                return None
            
            # Check if confirmation is required
            needs_confirmation = requires_confirmation(context.app_name)
            
            decision = AIDecision(
                chosen_option=chosen_option,
                confidence=0.8,  # TODO: Extract confidence from LLM
                reasoning=ai_response,
                requires_confirmation=needs_confirmation
            )
            
            logger.info(
                f"AI decision: '{chosen_option}' "
                f"(confirmation required: {needs_confirmation})"
            )
            
            return decision
        
        except Exception as e:
            logger.error(f"Error in AI decision: {e}")
            return None
    
    def _build_prompt(self, context: DialogContext) -> str:
        """
        Build the prompt for the LLM.
        
        Args:
            context: The dialog context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an intelligent macOS automation assistant. A dialog has appeared and you need to decide which action to take.

Application: {context.app_name}
Dialog Type: {context.dialog_type.value}
Question/Message: {context.question}
Available Options: {', '.join(context.options)}

Your task is to analyze this dialog and choose the most appropriate option. Consider:
1. The user's likely intent (e.g., saving work is usually preferred)
2. Safety (avoid destructive actions when uncertain)
3. Common sense (e.g., "Save" is usually better than "Don't Save")

Respond with ONLY the exact text of one of the available options. Do not add any explanation or additional text.

Your choice:"""
        
        return prompt
    
    def _match_option(self, ai_response: str, options: List[str]) -> Optional[str]:
        """
        Match the AI response to one of the available options.
        
        Args:
            ai_response: The response from the AI
            options: List of available options
            
        Returns:
            The matched option or None
        """
        ai_response_lower = ai_response.lower()
        
        # Try exact match first
        for option in options:
            if option.lower() == ai_response_lower:
                return option
        
        # Try partial match
        for option in options:
            if option.lower() in ai_response_lower or ai_response_lower in option.lower():
                return option
        
        return None
    
    def _decide_with_rules(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Use rule-based logic as a fallback when AI is not available.
        
        Args:
            context: The dialog context
            
        Returns:
            AIDecision object or None
        """
        # Simple rule-based logic
        options_lower = [opt.lower() for opt in context.options]
        
        # Prefer "Save" over "Don't Save"
        if "save" in options_lower or "enregistrer" in options_lower:
            chosen = context.options[
                next(i for i, opt in enumerate(options_lower) 
                     if "save" in opt or "enregistrer" in opt)
            ]
            return AIDecision(
                chosen_option=chosen,
                confidence=0.6,
                reasoning="Rule-based: Prefer saving work",
                requires_confirmation=True
            )
        
        # Prefer "Allow" over "Deny" for permissions
        if "allow" in options_lower or "autoriser" in options_lower:
            chosen = context.options[
                next(i for i, opt in enumerate(options_lower) 
                     if "allow" in opt or "autoriser" in opt)
            ]
            return AIDecision(
                chosen_option=chosen,
                confidence=0.5,
                reasoning="Rule-based: Allow permission (low confidence)",
                requires_confirmation=True
            )
        
        # Default: don't make a decision if unsure
        logger.warning("No rule matched, cannot make decision")
        return None
