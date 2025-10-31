"""
Integration tests for Sentry-AI.

These tests verify that all components work together correctly.
"""

import pytest
import time
from sentry_ai.agents import Observer, Analyzer, DecisionEngine, Actor
from sentry_ai.models.data_models import UIElement, DialogContext, DialogType, Action, ActionType


class TestEndToEndFlow:
    """Test the complete end-to-end flow."""
    
    def test_complete_flow_with_mock_data(self):
        """Test the complete flow from detection to action."""
        # Step 1: Create mock UI elements (simulating Observer output)
        elements = [
            UIElement(
                role="AXStaticText",
                title=None,
                value="Do you want to save changes to this document?"
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
        
        # Step 2: Analyze the dialog
        analyzer = Analyzer()
        context = analyzer.analyze("TextEdit", elements)
        
        assert context is not None
        assert context.app_name == "TextEdit"
        assert context.dialog_type == DialogType.SAVE_CONFIRMATION
        assert len(context.options) == 3
        
        # Step 3: Make a decision
        engine = DecisionEngine()
        decision = engine.decide(context)
        
        assert decision is not None
        assert decision.chosen_option in context.options
        
        # Step 4: Find the target element
        actor = Actor()
        target = actor.find_button_by_title(elements, decision.chosen_option)
        
        assert target is not None
        assert target.title == decision.chosen_option
        
        # Step 5: Create and execute action (in mock mode)
        action = Action(
            action_type=ActionType.CLICK_BUTTON,
            target_element=target
        )
        
        success = actor.execute(action)
        
        # In mock mode, this should always succeed
        assert success is True


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_log_action(self):
        """Test logging an action to the database."""
        from sentry_ai.core.database import db_manager
        
        log_id = db_manager.log_action(
            app_name="TestApp",
            dialog_type="save_confirmation",
            question="Save changes?",
            options=["Save", "Don't Save"],
            chosen_option="Save",
            success=True,
            execution_time_ms=150.5,
            ai_confidence=0.95
        )
        
        assert log_id is not None
        assert log_id > 0
    
    def test_get_statistics(self):
        """Test retrieving statistics."""
        from sentry_ai.core.database import db_manager
        
        stats = db_manager.get_statistics(days=7)
        
        assert "total_actions" in stats
        assert "successful_actions" in stats
        assert "success_rate" in stats
        assert isinstance(stats["total_actions"], int)


class TestOCRIntegration:
    """Test OCR integration."""
    
    def test_ocr_helper_initialization(self):
        """Test that OCR helper initializes correctly."""
        from sentry_ai.utils.ocr_helper import ocr_helper
        
        # Just check that it initializes without error
        assert ocr_helper is not None
    
    @pytest.mark.skipif(
        not hasattr(pytest, "config") or not pytest.config.getoption("--run-ocr"),
        reason="OCR tests require --run-ocr flag and macOS"
    )
    def test_ocr_text_extraction(self, tmp_path):
        """Test OCR text extraction (requires macOS)."""
        from sentry_ai.utils.ocr_helper import ocr_helper
        
        # This test would require a real image file
        # Skipped by default as it needs macOS environment
        pass


class TestAPIIntegration:
    """Test API integration."""
    
    def test_api_health_check(self):
        """Test API health check endpoint."""
        from fastapi.testclient import TestClient
        from sentry_ai.api.routes import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
    
    def test_api_get_status(self):
        """Test API status endpoint."""
        from fastapi.testclient import TestClient
        from sentry_ai.api.routes import app
        
        client = TestClient(app)
        response = client.get("/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "is_running" in data
        assert "observer_active" in data
    
    def test_api_get_config(self):
        """Test API config endpoint."""
        from fastapi.testclient import TestClient
        from sentry_ai.api.routes import app
        
        client = TestClient(app)
        response = client.get("/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "observer_interval" in data
        assert "ollama_model" in data
        assert "blacklist_apps" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
