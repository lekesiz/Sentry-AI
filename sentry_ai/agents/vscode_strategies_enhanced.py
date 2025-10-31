"""
Enhanced VS Code Strategies with Manus Search API.

This module extends the VS Code strategies with Manus Search API
to provide more intelligent and context-aware responses.
"""

from typing import Optional
from loguru import logger

from ..models.data_models import DialogContext, AIDecision
from .vscode_strategies import VSCodeStrategy, ClaudeQuestionStrategy
from ..core.llm_provider import LLMProviderFactory


class ClaudeQuestionStrategyWithSearch(VSCodeStrategy):
    """
    Enhanced strategy for Claude questions using Manus Search API.
    
    This strategy combines LLM responses with web search results
    to provide more accurate and up-to-date answers to Claude's questions.
    """
    
    def __init__(
        self,
        use_search: bool = True,
        search_first: bool = True,
        llm_provider: Optional[str] = None
    ):
        """
        Initialize the enhanced question strategy.
        
        Args:
            use_search: Whether to use Manus Search API
            search_first: Whether to search before using LLM
            llm_provider: LLM provider to use (if None, uses default)
        """
        self.use_search = use_search
        self.search_first = search_first
        self.llm_provider = LLMProviderFactory.create(llm_provider)
        logger.info(f"Enhanced question strategy initialized (search={use_search})")
    
    def can_handle(self, context: DialogContext) -> bool:
        """Check if this is a Claude question."""
        question = context.question or ""
        
        # Claude questions typically end with ?
        if question.strip().endswith("?"):
            # Exclude bash command and edit dialogs
            if "Allow this bash command" not in question and "Edit automatically" not in question:
                return True
        
        return False
    
    def decide(self, context: DialogContext) -> AIDecision:
        """
        Decide how to answer Claude's question.
        
        Uses Manus Search API to find relevant information,
        then uses LLM to generate a coherent answer.
        
        Args:
            context: The dialog context
            
        Returns:
            AIDecision with the answer
        """
        question = context.question or ""
        logger.info(f"Answering Claude question with search: {question[:50]}...")
        
        try:
            # Step 1: Search for relevant information (if enabled)
            search_results = None
            if self.use_search and self.search_first:
                search_results = self._search_for_answer(question)
            
            # Step 2: Generate answer using LLM
            if search_results:
                # Use search results as context
                answer = self._generate_answer_with_context(question, search_results)
            else:
                # Use LLM without search context
                answer = self._generate_answer(question)
            
            # Step 3: If search_first is False and we don't have a good answer, try search
            if not self.search_first and self.use_search and len(answer) < 50:
                search_results = self._search_for_answer(question)
                if search_results:
                    answer = self._generate_answer_with_context(question, search_results)
            
            return AIDecision(
                chosen_option=answer,
                reasoning=f"Answer generated using {'search + LLM' if search_results else 'LLM only'}",
                confidence=0.8 if search_results else 0.6,
                requires_confirmation=False
            )
        
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            # Fallback to simple LLM answer
            return self._generate_fallback_answer(question)
    
    def _search_for_answer(self, question: str) -> Optional[str]:
        """
        Search for relevant information using Manus Search API.
        
        Args:
            question: The question to search for
            
        Returns:
            Search results as string, or None if search fails
        """
        try:
            logger.debug(f"Searching for: {question}")
            
            # Note: This would use actual Manus search tool in production
            # For now, this is a template showing the structure
            
            # In production, this would be:
            # from manus_tools import search
            # 
            # results = search(
            #     queries=[question],
            #     type="info"
            # )
            # 
            # if results and len(results) > 0:
            #     # Combine top 3 results
            #     snippets = [r.get('snippet', '') for r in results[:3]]
            #     return "\n\n".join(snippets)
            
            logger.debug("[MOCK] Would search using Manus Search API")
            return None
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return None
    
    def _generate_answer_with_context(
        self,
        question: str,
        search_context: str
    ) -> str:
        """
        Generate an answer using LLM with search context.
        
        Args:
            question: The question to answer
            search_context: Context from search results
            
        Returns:
            Generated answer
        """
        try:
            prompt = f"""You are helping a developer answer a question from Claude AI assistant.

Question: {question}

Web search results:
{search_context}

Provide a concise, accurate answer based on the search results. Keep it under 100 words.

Answer:"""
            
            answer = self.llm_provider.generate(prompt, max_tokens=200)
            logger.info(f"Generated answer with search context: {answer[:50]}...")
            return answer
        
        except Exception as e:
            logger.error(f"Error generating answer with context: {e}")
            return self._generate_answer(question)
    
    def _generate_answer(self, question: str) -> str:
        """
        Generate an answer using LLM without search context.
        
        Args:
            question: The question to answer
            
        Returns:
            Generated answer
        """
        try:
            prompt = f"""You are helping a developer answer a question from Claude AI assistant.

Question: {question}

Provide a concise, helpful answer. Keep it under 100 words.

Answer:"""
            
            answer = self.llm_provider.generate(prompt, max_tokens=200)
            logger.info(f"Generated answer (no search): {answer[:50]}...")
            return answer
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "I need more information to answer that question."
    
    def _generate_fallback_answer(self, question: str) -> AIDecision:
        """
        Generate a fallback answer when all else fails.
        
        Args:
            question: The question to answer
            
        Returns:
            AIDecision with fallback answer
        """
        return AIDecision(
            chosen_option="Could you provide more details about that?",
            reasoning="Fallback answer due to error",
            confidence=0.3,
            requires_confirmation=False
        )


class ProjectContextStrategy(VSCodeStrategy):
    """
    Strategy that uses project context to answer questions.
    
    This strategy analyzes the current project files to provide
    context-aware answers to Claude's questions.
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize the project context strategy.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        logger.info(f"Project context strategy initialized (path={project_path})")
    
    def can_handle(self, context: DialogContext) -> bool:
        """Check if this question requires project context."""
        question = context.question or ""
        
        # Keywords that suggest project-specific questions
        project_keywords = [
            "database",
            "schema",
            "dependencies",
            "package",
            "structure",
            "architecture",
            "configuration",
            "env",
            "api",
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in project_keywords)
    
    def decide(self, context: DialogContext) -> AIDecision:
        """
        Answer question using project context.
        
        Args:
            context: The dialog context
            
        Returns:
            AIDecision with context-aware answer
        """
        question = context.question or ""
        logger.info(f"Answering with project context: {question[:50]}...")
        
        try:
            # Analyze project files
            project_info = self._analyze_project()
            
            # Generate answer based on project info
            answer = self._generate_contextual_answer(question, project_info)
            
            return AIDecision(
                chosen_option=answer,
                reasoning="Answer based on project analysis",
                confidence=0.9,
                requires_confirmation=False
            )
        
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            return AIDecision(
                chosen_option="I couldn't analyze the project. Could you be more specific?",
                reasoning=f"Error: {e}",
                confidence=0.3,
                requires_confirmation=False
            )
    
    def _analyze_project(self) -> dict:
        """
        Analyze project files to gather context.
        
        Uses Manus File API to read relevant files.
        
        Returns:
            Dictionary with project information
        """
        project_info = {}
        
        if not self.project_path:
            return project_info
        
        try:
            # In production, this would use Manus File API:
            # from manus_tools import file, match
            # 
            # # Find package.json
            # pkg_files = match(
            #     scope=f"{self.project_path}/**/package.json",
            #     action="glob"
            # )
            # 
            # if pkg_files:
            #     pkg_content = file(
            #         path=pkg_files[0],
            #         action="read"
            #     )
            #     project_info['dependencies'] = parse_package_json(pkg_content)
            # 
            # # Find database schema files
            # schema_files = match(
            #     scope=f"{self.project_path}/**/*.prisma",
            #     action="glob"
            # )
            # 
            # if schema_files:
            #     schema_content = file(
            #         path=schema_files[0],
            #         action="read"
            #     )
            #     project_info['database_schema'] = schema_content
            
            logger.debug("[MOCK] Would analyze project using Manus File API")
        
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
        
        return project_info
    
    def _generate_contextual_answer(
        self,
        question: str,
        project_info: dict
    ) -> str:
        """
        Generate an answer based on project context.
        
        Args:
            question: The question to answer
            project_info: Information about the project
            
        Returns:
            Contextual answer
        """
        if not project_info:
            return "I couldn't find relevant project information."
        
        # Build context from project info
        context_parts = []
        
        if 'dependencies' in project_info:
            deps = project_info['dependencies']
            context_parts.append(f"Dependencies: {', '.join(list(deps.keys())[:5])}")
        
        if 'database_schema' in project_info:
            context_parts.append("Database schema available")
        
        context = "\n".join(context_parts)
        
        # Use LLM to generate answer with context
        try:
            llm_provider = LLMProviderFactory.create()
            
            prompt = f"""Based on the project information below, answer this question:

Question: {question}

Project Context:
{context}

Provide a concise answer:"""
            
            answer = llm_provider.generate(prompt, max_tokens=200)
            return answer
        
        except Exception as e:
            logger.error(f"Error generating contextual answer: {e}")
            return f"Project info: {context}"


# Helper function to create enhanced strategy manager

def create_enhanced_strategy_manager(
    use_search: bool = True,
    project_path: Optional[str] = None
):
    """
    Create a strategy manager with enhanced strategies.
    
    Args:
        use_search: Whether to use Manus Search API
        project_path: Path to project for context analysis
        
    Returns:
        VSCodeStrategyManager with enhanced strategies
    """
    from .vscode_strategies import (
        VSCodeStrategyManager,
        ClaudeBashCommandStrategy,
        ClaudeEditAutomaticallyStrategy
    )
    
    manager = VSCodeStrategyManager()
    
    # Add enhanced strategies
    if use_search:
        manager.add_strategy(ClaudeQuestionStrategyWithSearch(use_search=True, llm_provider='ollama'))
    
    if project_path:
        manager.add_strategy(ProjectContextStrategy(project_path=project_path))
    
    logger.info(f"Enhanced strategy manager created (search={use_search}, project={bool(project_path)})")
    return manager
