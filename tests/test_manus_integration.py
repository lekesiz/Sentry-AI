"""
Tests for Manus API integration.

This module tests the integration of Manus Browser, Search, and File APIs
with Sentry-AI.
"""

import pytest
from pathlib import Path

from sentry_ai.agents.vscode_browser_observer import VSCodeBrowserObserver, is_browser_available
from sentry_ai.agents.vscode_browser_actor import VSCodeBrowserActor, execute_browser_action
from sentry_ai.agents.vscode_strategies_enhanced import (
    ClaudeQuestionStrategyWithSearch,
    ProjectContextStrategy,
    create_enhanced_strategy_manager
)
from sentry_ai.utils.project_analyzer import ProjectAnalyzer, analyze_project, get_project_summary
from sentry_ai.models.data_models import DialogContext, Action, ActionType


class TestVSCodeBrowserObserver:
    """Tests for VS Code Browser Observer."""
    
    def test_observer_initialization(self):
        """Test that browser observer initializes correctly."""
        observer = VSCodeBrowserObserver()
        assert observer is not None
        assert observer.vscode_urls is not None
        assert len(observer.vscode_urls) > 0
    
    def test_is_vscode_page_open(self):
        """Test VS Code page detection."""
        observer = VSCodeBrowserObserver()
        # Should not raise an error
        result = observer.is_vscode_page_open()
        assert isinstance(result, bool)
    
    def test_detect_claude_dialog_no_dialog(self):
        """Test dialog detection when no dialog is present."""
        observer = VSCodeBrowserObserver()
        dialog = observer.detect_claude_dialog()
        # Should return None when no page content
        assert dialog is None
    
    def test_hash_dialog(self):
        """Test dialog hashing for duplicate detection."""
        observer = VSCodeBrowserObserver()
        
        dialog = DialogContext(
            app_name="VS Code",
            question="Test question?",
            options=["Yes", "No"]
        )
        
        hash1 = observer._hash_dialog(dialog)
        hash2 = observer._hash_dialog(dialog)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length


class TestVSCodeBrowserActor:
    """Tests for VS Code Browser Actor."""
    
    def test_actor_initialization(self):
        """Test that browser actor initializes correctly."""
        actor = VSCodeBrowserActor()
        assert actor is not None
    
    def test_click_button_by_text(self):
        """Test clicking button by text."""
        actor = VSCodeBrowserActor()
        result = actor._click_button_by_text("Yes")
        # Should return True in mock mode
        assert result is True
    
    def test_type_text(self):
        """Test typing text."""
        actor = VSCodeBrowserActor()
        result = actor._type_text("Test answer")
        # Should return True in mock mode
        assert result is True
    
    def test_press_key(self):
        """Test pressing key."""
        actor = VSCodeBrowserActor()
        result = actor._press_key("Enter")
        # Should return True in mock mode
        assert result is True
    
    def test_execute_action_click(self):
        """Test executing click action."""
        actor = VSCodeBrowserActor()
        
        action = Action(
            action_type=ActionType.CLICK_BUTTON,
            target_element=None,
            parameters={"button_text": "Yes"}
        )
        
        result = actor.execute(action)
        assert result is True
    
    def test_execute_action_type(self):
        """Test executing type action."""
        actor = VSCodeBrowserActor()
        
        action = Action(
            action_type=ActionType.TYPE_TEXT,
            target_element=None,
            parameters={"text": "Test answer"}
        )
        
        result = actor.execute(action)
        assert result is True
    
    def test_execute_browser_action_helper(self):
        """Test the helper function for executing browser actions."""
        result = execute_browser_action("click", button_text="Yes")
        assert result is True
        
        result = execute_browser_action("type", text="Test")
        assert result is True
        
        result = execute_browser_action("press", key="Enter")
        assert result is True


class TestEnhancedStrategies:
    """Tests for enhanced VS Code strategies."""
    
    def test_question_strategy_with_search_initialization(self):
        """Test enhanced question strategy initialization."""
        strategy = ClaudeQuestionStrategyWithSearch(use_search=True, llm_provider='ollama')
        assert strategy is not None
        assert strategy.use_search is True
    
    def test_question_strategy_can_handle(self):
        """Test that strategy recognizes questions."""
        strategy = ClaudeQuestionStrategyWithSearch(use_search=False, llm_provider='ollama')
        
        context = DialogContext(
            app_name="VS Code",
            question="What database are you using?",
            options=[]
        )
        
        assert strategy.can_handle(context) is True
    
    def test_question_strategy_decide(self):
        """Test decision making with enhanced strategy."""
        strategy = ClaudeQuestionStrategyWithSearch(use_search=False, llm_provider='ollama')
        
        context = DialogContext(
            app_name="VS Code",
            question="What is your project structure?",
            options=[]
        )
        
        decision = strategy.decide(context)
        assert decision is not None
        assert decision.chosen_option is not None
        assert len(decision.chosen_option) > 0
    
    def test_project_context_strategy_initialization(self):
        """Test project context strategy initialization."""
        strategy = ProjectContextStrategy(project_path="/tmp/test")
        assert strategy is not None
        assert strategy.project_path == "/tmp/test"
    
    def test_project_context_strategy_can_handle(self):
        """Test that strategy recognizes project-related questions."""
        strategy = ProjectContextStrategy()
        
        # Should handle database questions
        context = DialogContext(
            app_name="VS Code",
            question="What is your database schema?",
            options=[]
        )
        assert strategy.can_handle(context) is True
        
        # Should handle dependency questions
        context = DialogContext(
            app_name="VS Code",
            question="What dependencies do you have?",
            options=[]
        )
        assert strategy.can_handle(context) is True
        
        # Should not handle generic questions
        context = DialogContext(
            app_name="VS Code",
            question="What is the weather?",
            options=[]
        )
        assert strategy.can_handle(context) is False
    
    def test_create_enhanced_strategy_manager(self):
        """Test creating enhanced strategy manager."""
        manager = create_enhanced_strategy_manager(
            use_search=True,
            project_path="/tmp/test"
        )
        
        assert manager is not None
        assert len(manager.strategies) > 0


class TestProjectAnalyzer:
    """Tests for Project Analyzer."""
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly."""
        analyzer = ProjectAnalyzer("/tmp/test")
        assert analyzer is not None
        assert analyzer.project_path == Path("/tmp/test")
    
    def test_detect_project_type(self):
        """Test project type detection."""
        # Create a temporary directory with package.json
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json
            pkg_json = Path(tmpdir) / "package.json"
            pkg_json.write_text('{"name": "test"}')
            
            analyzer = ProjectAnalyzer(tmpdir)
            project_type = analyzer._detect_project_type()
            
            assert project_type == "node"
    
    def test_analyze_dependencies(self):
        """Test dependency analysis."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json with dependencies
            pkg_json = Path(tmpdir) / "package.json"
            pkg_json.write_text('''{
                "dependencies": {"react": "^18.0.0"},
                "devDependencies": {"jest": "^29.0.0"}
            }''')
            
            analyzer = ProjectAnalyzer(tmpdir)
            deps = analyzer._analyze_dependencies()
            
            assert 'runtime' in deps
            assert 'react' in deps['runtime']
            assert 'dev' in deps
            assert 'jest' in deps['dev']
    
    def test_analyze_structure(self):
        """Test structure analysis."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some files
            (Path(tmpdir) / "index.js").write_text("// code")
            (Path(tmpdir) / "test.js").write_text("// test")
            (Path(tmpdir) / "config.json").write_text("{}")
            
            analyzer = ProjectAnalyzer(tmpdir)
            structure = analyzer._analyze_structure()
            
            assert structure['total_files'] == 3
            assert structure['source_files'] >= 1
            assert structure['test_files'] >= 1
            assert structure['config_files'] >= 1
    
    def test_get_summary(self):
        """Test getting project summary."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple Node.js project
            pkg_json = Path(tmpdir) / "package.json"
            pkg_json.write_text('{"name": "test", "dependencies": {"react": "^18.0.0"}}')
            
            analyzer = ProjectAnalyzer(tmpdir)
            summary = analyzer.get_summary()
            
            assert "Project Type: node" in summary
            assert "Runtime Dependencies" in summary
    
    def test_helper_functions(self):
        """Test helper functions."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_json = Path(tmpdir) / "package.json"
            pkg_json.write_text('{"name": "test"}')
            
            # Test analyze_project
            analysis = analyze_project(tmpdir)
            assert analysis is not None
            assert 'type' in analysis
            
            # Test get_project_summary
            summary = get_project_summary(tmpdir)
            assert summary is not None
            assert len(summary) > 0


class TestIntegration:
    """Integration tests for Manus API features."""
    
    def test_browser_observer_and_actor_workflow(self):
        """Test complete workflow with browser observer and actor."""
        observer = VSCodeBrowserObserver()
        actor = VSCodeBrowserActor()
        
        # Both should initialize without errors
        assert observer is not None
        assert actor is not None
    
    def test_enhanced_strategy_with_project_analyzer(self):
        """Test enhanced strategy using project analyzer."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a project
            pkg_json = Path(tmpdir) / "package.json"
            pkg_json.write_text('{"name": "test"}')
            
            # Create strategy with project path
            strategy = ProjectContextStrategy(project_path=tmpdir)
            
            # Test with a project-related question
            context = DialogContext(
                app_name="VS Code",
                question="What dependencies does this project have?",
                options=[]
            )
            
            decision = strategy.decide(context)
            assert decision is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
