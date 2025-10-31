"""
Decision Engine for Sentry-AI.

This module implements the Decision Engine that uses multiple LLM providers
(Ollama, Gemini, OpenAI, Claude) to make intelligent decisions about how to respond to dialogs.
"""

from typing import Optional, List
from loguru import logger

from ..models.data_models import DialogContext, AIDecision
from ..core.config import settings, requires_confirmation
from ..core.llm_provider import LLMProviderFactory, LLMProvider, BaseLLMProvider
from .vscode_strategies import VSCodeStrategyManager


class DecisionEngine:
    """
    Decision Engine that uses AI to decide how to respond to dialogs.
    
    Supports multiple LLM providers: Ollama, Gemini, OpenAI, Claude.
    Falls back to rule-based logic if AI is unavailable.
    """
    
    def __init__(self):
        """Initialize the Decision Engine."""
        self.llm_provider: Optional[BaseLLMProvider] = None
        self._initialize_llm()
        
        # Initialize VS Code strategy manager
        self.vscode_strategies = VSCodeStrategyManager(llm_provider=self.llm_provider)
    
    def _initialize_llm(self):
        """Initialize the configured LLM provider."""
        try:
            provider_name = settings.llm_provider.lower()
            provider_enum = LLMProvider(provider_name)
            
            # Get model from settings or use provider default
            model = settings.llm_model
            if not model and provider_name == "ollama":
                model = settings.ollama_model
            
            self.llm_provider = LLMProviderFactory.create(
                provider=provider_enum,
                model=model,
                temperature=settings.llm_temperature
            )
            
            if self.llm_provider.is_available():
                logger.info(f"LLM Provider initialized: {provider_name} with model {self.llm_provider.model}")
            else:
                logger.warning(f"LLM Provider {provider_name} not available. Using rule-based fallback.")
                self.llm_provider = None
        
        except ValueError as e:
            logger.error(f"Invalid LLM provider: {settings.llm_provider}. Using rule-based fallback.")
            self.llm_provider = None
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}. Using rule-based fallback.")
            self.llm_provider = None
    
    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Make a decision about how to respond to a dialog.
        
        Args:
            context: The dialog context to analyze
            
        Returns:
            AIDecision with the chosen option and reasoning, or None if no decision
        """
        # Check if this is a VS Code dialog - use specialized strategies
        if "visual studio code" in context.app_name.lower() or "vscode" in context.app_name.lower():
            decision = self.vscode_strategies.decide(context)
            if decision:
                logger.info(f"VS Code strategy decision: {decision.chosen_option}")
                return decision
        
        # Check if this app requires confirmation
        needs_confirmation = requires_confirmation(context.app_name)
        
        # Try AI decision first if available
        if self.llm_provider and self.llm_provider.is_available():
            try:
                decision = self._ai_decision(context)
                if decision:
                    decision.requires_confirmation = needs_confirmation
                    return decision
            except Exception as e:
                logger.error(f"AI decision failed: {e}. Falling back to rules.")
        
        # Fallback to rule-based decision
        decision = self._rule_based_decision(context)
        if decision:
            decision.requires_confirmation = needs_confirmation
        
        return decision
    
    def _ai_decision(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Use AI to make a decision.
        
        Args:
            context: Dialog context
            
        Returns:
            AIDecision or None
        """
        if not self.llm_provider:
            return None
        
        # Build prompt
        system_prompt = """You are an AI assistant helping to automate dialog responses on macOS.
Your task is to choose the most appropriate option based on the context.
Be conservative and prefer safe options (like Save over Don't Save)."""
        
        options = context.get_options
        prompt = f"""Application: {context.app_name}
Dialog Title: {context.window_title or context.dialog_title or 'Unknown'}
Dialog Text: {context.question or context.dialog_text or 'No text'}

Available options: {', '.join(options)}

Which option should I choose? Consider:
1. Safety (don't lose data)
2. User intent (what would the user likely want?)
3. Context (what was the user doing?)

Choose the option number and explain briefly."""
        
        try:
            result = self.llm_provider.generate_structured(
                prompt=prompt,
                options=options,
                system_prompt=system_prompt
            )
            
            return AIDecision(
                chosen_option=result["choice"],
                reasoning=result["reasoning"],
                confidence=result.get("confidence", 0.8),
                requires_confirmation=False  # Will be set by caller
            )
        
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None
    
    def _rule_based_decision(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Fallback rule-based decision logic.
        
        Args:
            context: Dialog context
            
        Returns:
            AIDecision or None
        """
        options = context.get_options
        if not options:
            return None
        
        # Common patterns
        save_keywords = ["save", "enregistrer", "sauvegarder", "yes", "oui"]
        cancel_keywords = ["cancel", "annuler", "no", "non"]
        
        # Try to match common patterns
        for option in options:
            option_lower = option.lower()
            
            # Prefer "Save" options
            if any(keyword in option_lower for keyword in save_keywords):
                return AIDecision(
                    chosen_option=option,
                    reasoning="Rule-based: Prefer saving to avoid data loss",
                    confidence=0.7,
                    requires_confirmation=False
                )
        
        # If no save option, prefer first non-cancel option
        for option in options:
            option_lower = option.lower()
            if not any(keyword in option_lower for keyword in cancel_keywords):
                return AIDecision(
                    chosen_option=option,
                    reasoning="Rule-based: Choose first non-cancel option",
                    confidence=0.6,
                    requires_confirmation=False
                )
        
        # Last resort: first option
        return AIDecision(
            chosen_option=options[0],
            reasoning="Rule-based: Default to first option",
            confidence=0.5,
            requires_confirmation=False
        )
    
    def match_option(self, target: str, options: List[str]) -> Optional[str]:
        """
        Find the best matching option for a target string.
        
        Args:
            target: Target string to match
            options: List of available options
            
        Returns:
            Best matching option or None
        """
        target_lower = target.lower()
        
        # Exact match
        for option in options:
            if option.lower() == target_lower:
                return option
        
        # Partial match
        for option in options:
            if target_lower in option.lower() or option.lower() in target_lower:
                return option
        
        return None
