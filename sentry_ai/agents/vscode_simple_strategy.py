"""
Simple VS Code Strategy - Always approve Claude Code dialogs.

This is a simplified version that automatically approves all VS Code dialogs
and provides simple "Yes" responses to Claude's questions.
"""

from typing import Optional
from loguru import logger

from ..models.data_models import DialogContext, AIDecision


class SimpleVSCodeStrategy:
    """
    Simple strategy that always approves VS Code / Claude Code dialogs.

    Perfect for users who want:
    - Automatic "Yes" to all prompts
    - No complex decision making
    - Just let Claude continue working
    """

    def __init__(self):
        logger.info("🎯 Simple VS Code Strategy: Auto-approve ALL dialogs")

    def can_handle(self, context: DialogContext) -> bool:
        """
        Check if this is a VS Code dialog.

        Returns True for ANY VS Code dialog.
        """
        app_name = (context.app_name or "").lower()

        # Match VS Code or Code
        if any(name in app_name for name in ["visual studio code", "code", "vscode"]):
            return True

        return False

    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Always return "Yes" or the most permissive option.

        Strategy:
        1. If "Yes" exists in options → Choose "Yes"
        2. If "Allow" exists → Choose "Allow"
        3. If "Continue" exists → Choose "Continue"
        4. If "OK" exists → Choose "OK"
        5. Otherwise → Choose first option
        """
        options = context.options or []

        if not options:
            logger.warning("No options available in dialog")
            return None

        # Normalize options to lowercase for comparison
        options_lower = [opt.lower() for opt in options]

        # Priority order: Yes > Allow > Continue > OK > Approve > First option
        priority_choices = [
            ("yes", "Yes"),
            ("allow", "Allow"),
            ("continue", "Continue"),
            ("ok", "OK"),
            ("approve", "Approve"),
        ]

        # Try each priority choice
        for keyword, button_text in priority_choices:
            for i, opt in enumerate(options_lower):
                if keyword in opt:
                    chosen = options[i]
                    logger.info(f"✅ Auto-approving with: {chosen}")

                    return AIDecision(
                        chosen_option=chosen,
                        reasoning=f"Simple strategy: Auto-approve with '{chosen}'",
                        confidence=1.0,
                        requires_confirmation=False
                    )

        # Fallback: Choose first option
        chosen = options[0]
        logger.info(f"✅ Auto-approving with first option: {chosen}")

        return AIDecision(
            chosen_option=chosen,
            reasoning=f"Simple strategy: Auto-approve with first option '{chosen}'",
            confidence=0.8,
            requires_confirmation=False
        )


class SimpleAnswerStrategy:
    """
    Strategy for answering Claude's questions automatically.

    When Claude asks a question, this strategy provides intelligent
    but simple answers to keep the workflow moving.
    """

    def __init__(self, llm_provider=None):
        """
        Initialize with optional LLM provider for intelligent answers.

        Args:
            llm_provider: Optional LLM provider for generating answers
        """
        self.llm_provider = llm_provider
        logger.info("🤖 Simple Answer Strategy: Auto-answer Claude's questions")

    def can_handle(self, context: DialogContext) -> bool:
        """Check if this is a question dialog from Claude."""
        question = (context.question or "").lower()
        options = [opt.lower() for opt in (context.options or [])]

        # Check if there's an input field or text response expected
        keywords = [
            "what", "how", "which", "where", "when", "who",
            "enter", "type", "specify", "provide", "tell"
        ]

        if any(keyword in question for keyword in keywords):
            # If there's an input field option
            if any("answer" in opt or "respond" in opt for opt in options):
                return True

        return False

    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Generate a simple answer to Claude's question.

        Uses LLM if available, otherwise provides smart defaults.
        """
        question = context.question or ""

        # Try using LLM for intelligent answer
        if self.llm_provider:
            try:
                answer = self._generate_llm_answer(question)
                if answer:
                    logger.info(f"🤖 Generated answer: {answer}")
                    return AIDecision(
                        chosen_option=answer,
                        reasoning=f"LLM-generated answer to: {question}",
                        confidence=0.9,
                        requires_confirmation=False
                    )
            except Exception as e:
                logger.warning(f"LLM answer failed: {e}, using default")

        # Fallback to smart defaults
        answer = self._generate_default_answer(question)
        logger.info(f"📝 Default answer: {answer}")

        return AIDecision(
            chosen_option=answer,
            reasoning=f"Default answer to: {question}",
            confidence=0.7,
            requires_confirmation=False
        )

    def _generate_llm_answer(self, question: str) -> Optional[str]:
        """Generate answer using LLM."""
        if not self.llm_provider:
            return None

        prompt = f"""The user is working with Claude Code in VS Code.
Claude asked: "{question}"

Provide a brief, helpful answer (max 50 words) to help Claude continue the task.
Be practical and assume the user wants to proceed with the task."""

        try:
            response = self.llm_provider.generate(prompt)

            # Extract answer from response
            if hasattr(response, 'answer'):
                return response.answer
            elif isinstance(response, dict) and 'answer' in response:
                return response['answer']
            elif isinstance(response, str):
                return response.strip()

            return None

        except Exception as e:
            logger.debug(f"LLM answer generation failed: {e}")
            return None

    def _generate_default_answer(self, question: str) -> str:
        """Generate a smart default answer based on question type."""
        question_lower = question.lower()

        # Common question patterns and default answers
        if "yes" in question_lower and "no" in question_lower:
            return "Yes"

        if "continue" in question_lower:
            return "Yes, continue"

        if "file" in question_lower or "path" in question_lower:
            return "./output.txt"  # Safe default file path

        if "name" in question_lower:
            return "output"  # Generic name

        if "number" in question_lower or "count" in question_lower:
            return "10"  # Reasonable default

        # Default generic answer
        return "Yes, proceed"


class SimpleVSCodeStrategyManager:
    """
    Manager for simple VS Code strategies.

    Coordinates between dialog approval and question answering.
    """

    def __init__(self, llm_provider=None):
        """
        Initialize with optional LLM provider.

        Args:
            llm_provider: Optional LLM provider for intelligent answers
        """
        self.approval_strategy = SimpleVSCodeStrategy()
        self.answer_strategy = SimpleAnswerStrategy(llm_provider)

        logger.info("✨ Simple VS Code Strategy Manager initialized")
        logger.info("   - Auto-approve: ON")
        logger.info("   - Auto-answer: ON")

    def decide(self, context: DialogContext) -> Optional[AIDecision]:
        """
        Make a decision using simple strategies.

        Args:
            context: Dialog context

        Returns:
            AIDecision or None
        """
        # Try approval strategy first (Yes/No buttons)
        if self.approval_strategy.can_handle(context):
            decision = self.approval_strategy.decide(context)
            if decision:
                logger.info(f"✅ Simple approval: {decision.chosen_option}")
                return decision

        # Try answer strategy for questions
        if self.answer_strategy.can_handle(context):
            decision = self.answer_strategy.decide(context)
            if decision:
                logger.info(f"🤖 Simple answer: {decision.chosen_option}")
                return decision

        # If nothing matched, default to "Yes" if available
        if context.options:
            for opt in context.options:
                if "yes" in opt.lower():
                    logger.info(f"✅ Default approval: {opt}")
                    return AIDecision(
                        chosen_option=opt,
                        reasoning="Default to Yes",
                        confidence=0.8,
                        requires_confirmation=False
                    )

        logger.debug("No simple strategy matched")
        return None
