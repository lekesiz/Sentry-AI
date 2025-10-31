"""
LLM Fallback Manager for Sentry-AI.

This module provides automatic fallback between multiple LLM providers
when one fails or is unavailable.
"""

from typing import List, Dict, Optional
from loguru import logger

from .llm_provider import (
    LLMProvider,
    BaseLLMProvider,
    OllamaProvider,
    GeminiProvider,
    OpenAIProvider,
    ClaudeProvider
)
from .config import settings


class LLMFallbackManager:
    """
    Manages automatic fallback between multiple LLM providers.
    
    Tries providers in order until one succeeds or all fail.
    """
    
    def __init__(
        self,
        fallback_order: Optional[List[str]] = None,
        enabled: bool = True
    ):
        """
        Initialize the fallback manager.
        
        Args:
            fallback_order: Order of providers to try (default from settings)
            enabled: Whether fallback is enabled
        """
        self.enabled = enabled
        self.fallback_order = fallback_order or settings.llm_fallback_order
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers."""
        logger.info("Initializing LLM providers for fallback...")
        
        # Initialize Ollama
        try:
            ollama = OllamaProvider(
                model=settings.ollama_model,
                temperature=settings.llm_temperature,
                host=settings.ollama_host
            )
            if ollama.is_available():
                self.providers[LLMProvider.OLLAMA] = ollama
                logger.info(f"✓ Ollama provider initialized ({settings.ollama_model})")
            else:
                logger.warning("✗ Ollama provider not available")
        except Exception as e:
            logger.warning(f"✗ Failed to initialize Ollama: {e}")
        
        # Initialize Gemini
        if settings.gemini_api_key:
            try:
                # Set API key in environment for GeminiProvider
                import os
                os.environ['GEMINI_API_KEY'] = settings.gemini_api_key
                
                gemini = GeminiProvider(
                    model=settings.llm_model or "gemini-2.0-flash-exp",
                    temperature=settings.llm_temperature
                )
                if gemini.is_available():
                    self.providers[LLMProvider.GEMINI] = gemini
                    logger.info("✓ Gemini provider initialized")
                else:
                    logger.warning("✗ Gemini provider not available")
            except Exception as e:
                logger.warning(f"✗ Failed to initialize Gemini: {e}")
        
        # Initialize OpenAI
        if settings.openai_api_key:
            try:
                # Set API key in environment for OpenAIProvider
                import os
                os.environ['OPENAI_API_KEY'] = settings.openai_api_key
                
                openai = OpenAIProvider(
                    model=settings.llm_model or "gpt-4o-mini",
                    temperature=settings.llm_temperature
                )
                if openai.is_available():
                    self.providers[LLMProvider.OPENAI] = openai
                    logger.info("✓ OpenAI provider initialized")
                else:
                    logger.warning("✗ OpenAI provider not available")
            except Exception as e:
                logger.warning(f"✗ Failed to initialize OpenAI: {e}")
        
        # Initialize Claude
        if settings.anthropic_api_key:
            try:
                # Set API key in environment for ClaudeProvider
                import os
                os.environ['ANTHROPIC_API_KEY'] = settings.anthropic_api_key
                
                claude = ClaudeProvider(
                    model=settings.llm_model or "claude-3-5-sonnet-20241022",
                    temperature=settings.llm_temperature
                )
                if claude.is_available():
                    self.providers[LLMProvider.CLAUDE] = claude
                    logger.info("✓ Claude provider initialized")
                else:
                    logger.warning("✗ Claude provider not available")
            except Exception as e:
                logger.warning(f"✗ Failed to initialize Claude: {e}")
        
        logger.info(f"Initialized {len(self.providers)} LLM provider(s)")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text with automatic fallback.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
            
        Raises:
            RuntimeError: If all providers fail
        """
        if not self.enabled or len(self.providers) == 0:
            raise RuntimeError("No LLM providers available")
        
        errors = []
        
        for provider_name in self.fallback_order:
            provider = self.providers.get(provider_name)
            
            if not provider:
                continue
            
            try:
                logger.info(f"Trying {provider_name} provider...")
                response = provider.generate(prompt, system_prompt)
                logger.success(f"✓ {provider_name} succeeded")
                return response
            
            except Exception as e:
                error_msg = f"{provider_name} failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
                continue
        
        # All providers failed
        error_summary = "; ".join(errors)
        raise RuntimeError(f"All LLM providers failed: {error_summary}")
    
    def generate_structured(
        self,
        prompt: str,
        options: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate structured response with automatic fallback.
        
        Args:
            prompt: User prompt
            options: List of available options
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with 'choice' and 'reasoning'
            
        Raises:
            RuntimeError: If all providers fail
        """
        if not self.enabled or len(self.providers) == 0:
            raise RuntimeError("No LLM providers available")
        
        errors = []
        
        for provider_name in self.fallback_order:
            provider = self.providers.get(provider_name)
            
            if not provider:
                continue
            
            try:
                logger.info(f"Trying {provider_name} provider...")
                response = provider.generate_structured(prompt, options, system_prompt)
                logger.success(f"✓ {provider_name} succeeded")
                return response
            
            except Exception as e:
                error_msg = f"{provider_name} failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
                continue
        
        # All providers failed
        error_summary = "; ".join(errors)
        raise RuntimeError(f"All LLM providers failed: {error_summary}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of currently available providers."""
        return list(self.providers.keys())
    
    def is_any_available(self) -> bool:
        """Check if any provider is available."""
        return len(self.providers) > 0


# Global fallback manager instance
fallback_manager = LLMFallbackManager()
