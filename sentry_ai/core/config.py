"""
Configuration module for Sentry-AI.

This module handles all configuration settings for the application,
including environment variables, application settings, and security policies.
"""

from typing import List, Optional
import json
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application Info
    app_name: str = "Sentry-AI"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # LLM Configuration
    llm_provider: str = Field(default="ollama", description="LLM provider to use (ollama, gemini, openai, claude)")
    llm_model: Optional[str] = Field(default=None, description="Model name (provider-specific, None for default)")
    llm_temperature: float = Field(default=0.1, ge=0.0, le=1.0, description="LLM temperature for decision making")
    
    # Ollama Configuration (when using ollama provider)
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama API endpoint")
    ollama_model: str = Field(default="phi3:mini", description="Ollama model to use")
    
    # API Keys (optional, set via environment variables)
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic Claude API key")
    
    # LLM Fallback Configuration
    llm_fallback_enabled: bool = Field(default=True, description="Enable automatic fallback to other providers")
    llm_fallback_order: List[str] = Field(
        default=["claude", "openai", "gemini", "ollama"],
        description="Order of LLM providers to try (fallback chain)"
    )
    
    # Observer Settings
    observer_interval: float = Field(default=2.0, ge=0.5, description="Polling interval in seconds")
    observer_enabled: bool = True
    event_driven_mode: bool = Field(default=True, description="Use event-driven observer instead of polling")
    
    # Security Settings
    blacklist_apps: List[str] = Field(
        default=[
            "Terminal",
            "iTerm",
            "Keychain Access",
            "System Preferences",
            "System Settings",
            "Activity Monitor",
            "Disk Utility",
        ],
        description="Applications that should never be automated"
    )
    
    whitelist_apps: Optional[List[str]] = Field(
        default=None,
        description="If set, only these applications will be automated"
    )
    
    require_confirmation_for: List[str] = Field(
        default=["Finder", "Mail"],
        description="Applications that require user confirmation before action"
    )
    
    # Database Settings
    database_url: str = Field(
        default="sqlite:///./sentry_ai.db",
        description="Database connection URL"
    )
    
    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="sentry_ai.log", description="Log file path")
    log_retention_days: int = Field(default=30, description="Number of days to keep logs")
    
    # API Settings
    api_host: str = Field(default="127.0.0.1", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    @field_validator('blacklist_apps', 'whitelist_apps', 'require_confirmation_for', 'llm_fallback_order', mode='before')
    @classmethod
    def parse_json_list(cls, v):
        """
        Parse JSON array strings from .env file.
        
        Pydantic doesn't automatically parse JSON arrays from .env,
        so we need to manually convert strings like '["Terminal"]' to lists.
        """
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [parsed]  # Single value, wrap in list
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, treat as comma-separated values
                return [x.strip() for x in v.split(',') if x.strip()]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()


def is_app_allowed(app_name: str) -> bool:
    """
    Check if an application is allowed to be automated.
    
    Args:
        app_name: Name of the application to check
        
    Returns:
        True if the app can be automated, False otherwise
    """
    # Check blacklist first
    if app_name in settings.blacklist_apps:
        return False
    
    # If whitelist is set, only allow whitelisted apps
    if settings.whitelist_apps is not None:
        return app_name in settings.whitelist_apps
    
    # Otherwise, allow by default
    return True


def requires_confirmation(app_name: str) -> bool:
    """
    Check if an application requires user confirmation before automation.
    
    Args:
        app_name: Name of the application to check
        
    Returns:
        True if confirmation is required, False otherwise
    """
    return app_name in settings.require_confirmation_for
