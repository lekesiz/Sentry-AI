"""
Tests for VS Code integration.

This module tests the VS Code Observer, strategies, and decision engine integration.
"""

import pytest
from sentry_ai.agents.vscode_observer import VSCodeObserver
from sentry_ai.agents.vscode_strategies import (
    ClaudeBashCommandStrategy,
    ClaudeEditAutomaticallyStrategy,
    VSCodeStrategyManager
)
from sentry_ai.agents.decision_engine import DecisionEngine
from sentry_ai.models.data_models import DialogContext, UIElement


class TestVSCodeObserver:
    """Tests for VS Code Observer."""
    
    def test_observer_initialization(self):
        """Test that VS Code Observer initializes correctly."""
        observer = VSCodeObserver()
        assert observer is not None
        assert observer.vscode_bundle_ids is not None
        assert len(observer.vscode_bundle_ids) > 0
    
    def test_is_vscode_running(self):
        """Test VS Code running detection."""
        observer = VSCodeObserver()
        # This will return False in sandbox, but should not raise an error
        result = observer.is_vscode_running()
        assert isinstance(result, bool)


class TestClaudeBashCommandStrategy:
    """Tests for Claude bash command strategy."""
    
    def test_can_handle_bash_command_dialog(self):
        """Test that strategy recognizes bash command dialogs."""
        strategy = ClaudeBashCommandStrategy()
        
        context = DialogContext(
            app_name="Visual Studio Code",
            question="Allow this bash command?\n\n$ ls -la",
            options=["Yes", "Yes, and don't ask again", "No", "Tell Claude what to do instead"]
        )
        
        assert strategy.can_handle(context) is True
    
    def test_approve_safe_command(self):
        """Test that safe commands are approved."""
        strategy = ClaudeBashCommandStrategy(auto_approve=True, safe_commands_only=True)
        
        context = DialogContext(
            app_name="Visual Studio Code",
            question="Allow this bash command?\n\n$ ls -la",
            options=["Yes", "No"]
        )
        
        decision = strategy.decide(context)
        assert decision is not None
        assert decision.chosen_option == "Yes"
        assert "safe" in decision.reasoning.lower()
    
    def test_reject_dangerous_command(self):
        """Test that dangerous commands are rejected."""
        strategy = ClaudeBashCommandStrategy(auto_approve=True, safe_commands_only=True)
        
        context = DialogContext(
            app_name="Visual Studio Code",
            question="Allow this bash command?\n\n$ rm -rf /",
            options=["Yes", "No"]
        )
        
        decision = strategy.decide(context)
        assert decision is not None
        assert decision.chosen_option == "No"
        assert "dangerous" in decision.reasoning.lower()


class TestClaudeEditAutomaticallyStrategy:
    """Tests for Claude edit automatically strategy."""
    
    def test_can_handle_edit_dialog(self):
        """Test that strategy recognizes edit dialogs."""
        strategy = ClaudeEditAutomaticallyStrategy()
        
        context = DialogContext(
            app_name="Visual Studio Code",
            question="Edit automatically?",
            options=["Yes", "No"]
        )
        
        assert strategy.can_handle(context) is True
    
    def test_approve_edit(self):
        """Test that edits are approved when auto_approve is True."""
        strategy = ClaudeEditAutomaticallyStrategy(auto_approve=True)
        
        context = DialogContext(
            app_name="Visual Studio Code",
            question="Edit automatically?",
            options=["Yes", "No"]
        )
        
        decision = strategy.decide(context)
        assert decision is not None
        assert decision.chosen_option == "Yes"


class TestVSCodeStrategyManager:
    """Tests for VS Code Strategy Manager."""
    
    def test_manager_initialization(self):
        """Test that manager initializes with strategies."""
        manager = VSCodeStrategyManager()
        assert manager is not None
        assert len(manager.strategies) > 0
    
    def test_manager_finds_correct_strategy(self):
        """Test that manager finds the correct strategy for a dialog."""
        manager = VSCodeStrategyManager()
        
        context = DialogContext(
            app_name="Visual Studio Code",
            question="Allow this bash command?\n\n$ cat file.txt",
            options=["Yes", "No"]
        )
        
        decision = manager.decide(context)
        assert decision is not None
        assert decision.chosen_option == "Yes"


class TestDecisionEngineVSCodeIntegration:
    """Tests for Decision Engine VS Code integration."""
    
    def test_decision_engine_uses_vscode_strategies(self):
        """Test that Decision Engine uses VS Code strategies for VS Code dialogs."""
        engine = DecisionEngine()
        
        context = DialogContext(
            app_name="Visual Studio Code",
            question="Allow this bash command?\n\n$ pwd",
            options=["Yes", "No"]
        )
        
        decision = engine.decide(context)
        assert decision is not None
        # Should use VS Code strategy, not generic strategy
        assert decision.chosen_option == "Yes"
    
    def test_decision_engine_fallback_for_non_vscode(self):
        """Test that Decision Engine uses fallback for non-VS Code dialogs."""
        engine = DecisionEngine()
        
        context = DialogContext(
            app_name="TextEdit",
            dialog_title="Save changes?",
            dialog_text="Do you want to save?",
            available_options=["Save", "Don't Save", "Cancel"]
        )
        
        decision = engine.decide(context)
        assert decision is not None
        # Should use fallback strategy
        assert decision.chosen_option == "Save"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
