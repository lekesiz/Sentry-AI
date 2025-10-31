"""
Tests for Sentry-AI agents.
"""

import pytest
from sentry_ai.agents import Analyzer, DecisionEngine
from sentry_ai.models.data_models import UIElement, DialogContext, DialogType


class TestAnalyzer:
    """Tests for the Analyzer agent."""
    
    def test_analyze_save_dialog(self):
        """Test analyzing a save confirmation dialog."""
        analyzer = Analyzer()
        
        # Create mock UI elements
        elements = [
            UIElement(
                role="AXStaticText",
                title=None,
                value="Do you want to save changes?"
            ),
            UIElement(
                role="AXButton",
                title="Save",
                value=None
            ),
            UIElement(
                role="AXButton",
                title="Don't Save",
                value=None
            ),
            UIElement(
                role="AXButton",
                title="Cancel",
                value=None
            )
        ]
        
        context = analyzer.analyze("TextEdit", elements)
        
        assert context is not None
        assert context.app_name == "TextEdit"
        assert context.dialog_type == DialogType.SAVE_CONFIRMATION
        assert len(context.options) == 3
        assert "Save" in context.options
        assert "Don't Save" in context.options
    
    def test_analyze_no_buttons(self):
        """Test that analyzer returns None when no buttons are found."""
        analyzer = Analyzer()
        
        elements = [
            UIElement(
                role="AXStaticText",
                title=None,
                value="This is just text"
            )
        ]
        
        context = analyzer.analyze("TestApp", elements)
        
        assert context is None


class TestDecisionEngine:
    """Tests for the Decision Engine."""
    
    def test_rule_based_decision_save(self):
        """Test rule-based decision for save dialog."""
        engine = DecisionEngine()
        
        context = DialogContext(
            app_name="TextEdit",
            dialog_type=DialogType.SAVE_CONFIRMATION,
            question="Do you want to save changes?",
            options=["Save", "Don't Save", "Cancel"],
            elements=[]
        )
        
        # Force rule-based decision
        decision = engine._decide_with_rules(context)
        
        assert decision is not None
        assert decision.chosen_option == "Save"
        assert decision.requires_confirmation is True
    
    def test_match_option_exact(self):
        """Test exact option matching."""
        engine = DecisionEngine()
        
        options = ["Save", "Don't Save", "Cancel"]
        
        matched = engine._match_option("Save", options)
        assert matched == "Save"
        
        matched = engine._match_option("save", options)
        assert matched == "Save"
    
    def test_match_option_partial(self):
        """Test partial option matching."""
        engine = DecisionEngine()
        
        options = ["Save", "Don't Save", "Cancel"]
        
        matched = engine._match_option("I would save", options)
        assert matched == "Save"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
