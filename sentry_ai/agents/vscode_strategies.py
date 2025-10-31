"""
VS Code Decision Strategies for Sentry-AI.

This module implements specialized decision strategies for VS Code and Claude Code dialogs.
"""

from typing import Optional, Dict, List
from loguru import logger

from ..models.data_models import DialogContext, AIDecision


class VSCodeStrategy:
    """Base class for VS Code decision strategies."""
    
    def can_handle(self, context: DialogContext) -> bool:
        """Check if this strategy can handle the dialog."""
        raise NotImplementedError
    
    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """Make a decision for the dialog."""
        raise NotImplementedError


class ClaudeBashCommandStrategy(VSCodeStrategy):
    """
    Strategy for handling Claude Code bash command approval dialogs.
    
    Example dialog:
    - "Allow this bash command?"
    - Options: ["Yes", "Yes, and don't ask again", "No", "Tell Claude what to do instead"]
    """
    
    def __init__(self, auto_approve: bool = True, safe_commands_only: bool = True):
        """
        Initialize the strategy.
        
        Args:
            auto_approve: Automatically approve commands
            safe_commands_only: Only approve safe commands
        """
        self.auto_approve = auto_approve
        self.safe_commands_only = safe_commands_only
        
        # Safe command patterns
        self.safe_patterns = [
            "cat", "ls", "pwd", "echo", "grep", "find", "wc",
            "head", "tail", "less", "more", "which", "whereis",
            "python", "node", "npm", "pip", "git status", "git log",
            "git diff", "curl", "wget"
        ]
        
        # Dangerous command patterns
        self.dangerous_patterns = [
            "rm -rf", "sudo", "chmod", "chown", "dd", "mkfs",
            "format", ">", ">>", "kill", "pkill", "killall"
        ]
    
    def can_handle(self, context: DialogContext) -> bool:
        """Check if this is a bash command approval dialog."""
        question = (context.question or "").lower()
        options = [opt.lower() for opt in (context.options or [])]
        
        # Check for bash command keywords
        if "allow this bash command" in question or "allow this command" in question:
            return True
        
        # Check button options
        if "yes" in options and "no" in options:
            if any("tell claude" in opt for opt in options):
                return True
        
        return False
    
    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """Decide whether to approve the bash command."""
        if not self.auto_approve:
            return AIDecision(
                chosen_option="No",
                reasoning="Auto-approve disabled",
                confidence=1.0,
                requires_confirmation=True
            )
        
        # Extract command from question
        command = self._extract_command(context.question or "")
        
        if self.safe_commands_only:
            if self._is_dangerous_command(command):
                return AIDecision(
                    chosen_option="No",
                    reasoning=f"Dangerous command detected: {command}",
                    confidence=0.9,
                    requires_confirmation=True
                )
            
            if not self._is_safe_command(command):
                return AIDecision(
                    chosen_option="Tell Claude what to do instead",
                    reasoning=f"Unknown command safety: {command}",
                    confidence=0.7,
                    requires_confirmation=True
                )
        
        # Approve safe command
        # Prefer "Yes" over "Yes, and don't ask again" for safety
        options = context.options or []
        if "Yes" in options:
            return AIDecision(
                chosen_option="Yes",
                reasoning=f"Safe command approved: {command}",
                confidence=0.9,
                requires_confirmation=False
            )
        
        return None
    
    def _extract_command(self, question: str) -> str:
        """Extract the command from the question text."""
        # Try to find command in question
        # Usually formatted like: "Allow this bash command?\n\n$ command here"
        lines = question.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('$'):
                return line[1:].strip()
            if line and not line.endswith('?'):
                return line
        
        return ""
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if a command is in the safe list."""
        command_lower = command.lower()
        return any(pattern in command_lower for pattern in self.safe_patterns)
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if a command is dangerous."""
        command_lower = command.lower()
        return any(pattern in command_lower for pattern in self.dangerous_patterns)


class ClaudeEditAutomaticallyStrategy(VSCodeStrategy):
    """
    Strategy for handling Claude Code "Edit automatically" dialogs.
    
    Example dialog:
    - "Edit automatically?"
    - Options: ["Yes", "No"]
    """
    
    def __init__(self, auto_approve: bool = True):
        """
        Initialize the strategy.
        
        Args:
            auto_approve: Automatically approve edit requests
        """
        self.auto_approve = auto_approve
    
    def can_handle(self, context: DialogContext) -> bool:
        """Check if this is an edit automatically dialog."""
        question = (context.question or "").lower()
        return "edit automatically" in question
    
    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """Decide whether to allow automatic editing."""
        if self.auto_approve:
            return AIDecision(
                chosen_option="Yes",
                reasoning="Auto-edit approved",
                confidence=0.8,
                requires_confirmation=False
            )
        else:
            return AIDecision(
                chosen_option="No",
                reasoning="Auto-edit disabled",
                confidence=1.0,
                requires_confirmation=True
            )


class ClaudeQuestionStrategy(VSCodeStrategy):
    """
    Strategy for handling Claude Code questions that require text input.
    
    Example dialog:
    - Claude asks a question
    - User needs to provide text answer
    """
    
    def __init__(self, llm_provider=None):
        """
        Initialize the strategy.
        
        Args:
            llm_provider: LLM provider for generating answers
        """
        self.llm_provider = llm_provider
    
    def can_handle(self, context: DialogContext) -> bool:
        """Check if this is a question dialog."""
        question = (context.question or "").lower()
        
        # Check if question ends with "?"
        if question.strip().endswith('?'):
            # Check if there are no button options (text input expected)
            if not context.options or len(context.options) == 0:
                return True
        
        return False
    
    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """Generate an answer to Claude's question."""
        if not self.llm_provider:
            return AIDecision(
                chosen_option="",
                reasoning="No LLM provider available for answering questions",
                confidence=0.0,
                requires_confirmation=True
            )
        
        # Use LLM to generate answer
        try:
            prompt = f"""Claude Code is asking a question about the project:

Question: {context.question}

Provide a brief, helpful answer that will help Claude continue the development task."""
            
            answer = self.llm_provider.generate(prompt)
            
            return AIDecision(
                chosen_option=answer,
                reasoning="LLM-generated answer to Claude's question",
                confidence=0.7,
                requires_confirmation=True  # Always confirm AI-generated answers
            )
        
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return None


class VSCodeStrategyManager:
    """Manager for VS Code decision strategies."""
    
    def __init__(self, llm_provider=None):
        """
        Initialize the strategy manager.
        
        Args:
            llm_provider: LLM provider for strategies that need it
        """
        self.strategies: List[VSCodeStrategy] = [
            ClaudeBashCommandStrategy(auto_approve=True, safe_commands_only=True),
            ClaudeEditAutomaticallyStrategy(auto_approve=True),
            ClaudeQuestionStrategy(llm_provider=llm_provider)
        ]
    
    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Find appropriate strategy and make decision.
        
        Args:
            context: Dialog context
            
        Returns:
            AIDecision or None
        """
        for strategy in self.strategies:
            if strategy.can_handle(context):
                logger.info(f"Using strategy: {strategy.__class__.__name__}")
                return strategy.decide(context)
        
        logger.warning("No strategy found for dialog")
        return None
    
    def add_strategy(self, strategy: VSCodeStrategy):
        """Add a custom strategy."""
        self.strategies.insert(0, strategy)  # Add at beginning for priority
    
    def remove_strategy(self, strategy_class):
        """Remove a strategy by class."""
        self.strategies = [s for s in self.strategies if not isinstance(s, strategy_class)]
