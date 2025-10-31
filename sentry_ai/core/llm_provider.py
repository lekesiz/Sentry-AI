"""
LLM Provider module for Sentry-AI.

This module provides a unified interface for multiple LLM providers:
- Ollama (local)
- Google Gemini
- OpenAI
- Anthropic Claude

Each provider implements the same interface for seamless switching.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from enum import Enum
import os
from loguru import logger

from .llm_parser import parse_structured_response


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model: str, temperature: float = 0.1):
        """
        Initialize the LLM provider.
        
        Args:
            model: Model name/identifier
            temperature: Sampling temperature (0.0-1.0)
        """
        self.model = model
        self.temperature = temperature
        self._available = False
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        options: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate a structured response (for decision making).
        
        Args:
            prompt: User prompt
            options: List of available options
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with 'choice' and 'reasoning' keys
        """
        pass


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, model: str = "phi3:mini", temperature: float = 0.1, host: str = "http://localhost:11434"):
        super().__init__(model, temperature)
        self.host = host
        try:
            import ollama
            self.client = ollama
            self._available = True
        except ImportError:
            logger.warning("Ollama package not installed")
            self._available = False
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        if not self._available:
            return False
        
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Ollama."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": self.temperature}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    def generate_structured(
        self,
        prompt: str,
        options: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate structured decision using Ollama."""
        full_prompt = f"{prompt}\n\nAvailable options:\n"
        for i, option in enumerate(options, 1):
            full_prompt += f"{i}. {option}\n"
        full_prompt += "\nRespond with ONLY the number of your choice and a brief reason."
        
        response = self.generate(full_prompt, system_prompt)
        return parse_structured_response(response, options, confidence=0.8)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, model: str = "gemini-2.0-flash-exp", temperature: float = 0.1):
        super().__init__(model, temperature)
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set")
            self._available = False
            return
        
        try:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=self.api_key)
            self.types = types
            self._available = True
        except ImportError:
            logger.warning("google-genai package not installed")
            self._available = False
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self._available and self.api_key is not None
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Gemini."""
        try:
            config = self.types.GenerateContentConfig(
                temperature=self.temperature,
                system_instruction=system_prompt if system_prompt else None
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    def generate_structured(
        self,
        prompt: str,
        options: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate structured decision using Gemini."""
        full_prompt = f"{prompt}\n\nAvailable options:\n"
        for i, option in enumerate(options, 1):
            full_prompt += f"{i}. {option}\n"
        full_prompt += "\nRespond with ONLY the number of your choice and a brief reason."
        
        response = self.generate(full_prompt, system_prompt)
        return parse_structured_response(response, options, confidence=0.9)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.1):
        super().__init__(model, temperature)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set")
            self._available = False
            return
        
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base if self.api_base else None
            )
            self._available = True
        except ImportError:
            logger.warning("openai package not installed")
            self._available = False
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self._available and self.api_key is not None
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    def generate_structured(
        self,
        prompt: str,
        options: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate structured decision using OpenAI."""
        full_prompt = f"{prompt}\n\nAvailable options:\n"
        for i, option in enumerate(options, 1):
            full_prompt += f"{i}. {option}\n"
        full_prompt += "\nRespond with ONLY the number of your choice and a brief reason."
        
        response = self.generate(full_prompt, system_prompt)
        return parse_structured_response(response, options, confidence=0.95)


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.1):
        super().__init__(model, temperature)
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set")
            self._available = False
            return
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            self._available = True
        except ImportError:
            logger.warning("anthropic package not installed")
            self._available = False
    
    def is_available(self) -> bool:
        """Check if Claude is available."""
        return self._available and self.api_key is not None
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Claude."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=self.temperature,
                system=system_prompt if system_prompt else "You are a helpful AI assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise
    
    def generate_structured(
        self,
        prompt: str,
        options: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate structured decision using Claude."""
        full_prompt = f"{prompt}\n\nAvailable options:\n"
        for i, option in enumerate(options, 1):
            full_prompt += f"{i}. {option}\n"
        full_prompt += "\nRespond with ONLY the number of your choice and a brief reason."
        
        response = self.generate(full_prompt, system_prompt)
        return parse_structured_response(response, options, confidence=0.95)


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def create(provider: LLMProvider, model: Optional[str] = None, temperature: float = 0.1) -> BaseLLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider: Provider type
            model: Optional model override
            temperature: Sampling temperature
            
        Returns:
            LLM provider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider == LLMProvider.OLLAMA:
            return OllamaProvider(model or "phi3:mini", temperature)
        elif provider == LLMProvider.GEMINI:
            return GeminiProvider(model or "gemini-2.0-flash-exp", temperature)
        elif provider == LLMProvider.OPENAI:
            return OpenAIProvider(model or "gpt-4o-mini", temperature)
        elif provider == LLMProvider.CLAUDE:
            return ClaudeProvider(model or "claude-3-5-sonnet-20241022", temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def get_available_providers() -> List[LLMProvider]:
        """
        Get list of available (configured) providers.
        
        Returns:
            List of available provider types
        """
        available = []
        
        for provider in LLMProvider:
            try:
                instance = LLMProviderFactory.create(provider)
                if instance.is_available():
                    available.append(provider)
            except Exception as e:
                logger.debug(f"Provider {provider} not available: {e}")
        
        return available
