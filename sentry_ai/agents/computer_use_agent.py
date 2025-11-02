"""
Computer Use Agent for Sentry-AI

This agent uses Anthropic's Computer Use API to:
1. Take screenshots
2. Analyze screen with vision AI
3. Control mouse and keyboard
4. Automate tasks based on visual understanding
"""

import base64
import io
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

import pyautogui
import mss
from PIL import Image
from loguru import logger

from anthropic import Anthropic
from ..core.config import settings


class ComputerUseAgent:
    """
    Agent that can see and interact with the computer screen.

    Capabilities:
    - Screenshot capture
    - Vision-based analysis
    - Mouse control (click, move, drag)
    - Keyboard control (type, press keys)
    - Automated task execution
    """

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize Computer Use Agent

        Args:
            anthropic_api_key: Anthropic API key (uses settings if not provided)
        """
        self.api_key = anthropic_api_key or settings.anthropic_api_key

        if not self.api_key:
            raise ValueError("Anthropic API key required for Computer Use")

        self.client = Anthropic(api_key=self.api_key)

        # Safety settings
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.5  # Pause between actions

        logger.info("🖥️  Computer Use Agent initialized")
        logger.info(f"   - Screen size: {pyautogui.size()}")
        logger.info(f"   - Failsafe: ON (move to corner to abort)")

    def capture_screen(self, region: Optional[Dict[str, int]] = None) -> Image.Image:
        """
        Capture screenshot of entire screen or specific region

        Args:
            region: Optional dict with 'left', 'top', 'width', 'height'

        Returns:
            PIL Image object
        """
        with mss.mss() as sct:
            if region:
                monitor = region
            else:
                # Capture primary monitor
                monitor = sct.monitors[1]

            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

            logger.debug(f"📸 Screenshot captured: {img.size}")
            return img

    def image_to_base64(self, image: Image.Image, format: str = "PNG") -> str:
        """
        Convert PIL Image to base64 string

        Args:
            image: PIL Image
            format: Image format (PNG, JPEG)

        Returns:
            Base64 encoded string
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')

    def analyze_screen(self, task_description: str, screenshot: Optional[Image.Image] = None) -> Dict[str, Any]:
        """
        Analyze screen with Claude's vision capabilities

        Args:
            task_description: What to look for or do
            screenshot: Optional pre-captured screenshot

        Returns:
            Dict with analysis results and recommended actions
        """
        if screenshot is None:
            screenshot = self.capture_screen()

        # Convert to base64
        img_base64 = self.image_to_base64(screenshot)

        logger.info(f"🤖 Analyzing screen: {task_description}")

        # Use Claude with vision (latest Opus 4 model)
        response = self.client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": f"""Analyze this screenshot and help with the following task:

{task_description}

IMPORTANT: Respond ONLY with valid JSON. No markdown, no code blocks, just raw JSON.

Format your response as JSON:
{{
    "analysis": "description of what you see",
    "ui_elements": [
        {{"type": "button", "text": "Yes", "location": "center-right"}}
    ],
    "recommended_action": {{
        "type": "click",
        "target": "Yes",
        "coordinates": {{"x": 0.65, "y": 0.68}}
    }},
    "confidence": 0.95
}}

For coordinates:
- x and y must be PERCENTAGES between 0.0 and 1.0
- x=0.5 is horizontal center, y=0.5 is vertical center
- Example: A button in bottom-right would be {{"x": 0.75, "y": 0.85}}
- Measure carefully from the screenshot edges

Common button locations:
- "Yes" button: usually around {{"x": 0.65, "y": 0.68}}
- "No" button: usually around {{"x": 0.50, "y": 0.68}}
- "Cancel" button: usually around {{"x": 0.35, "y": 0.68}}

RESPOND WITH ONLY RAW JSON, NO MARKDOWN!"""
                        }
                    ]
                }
            ]
        )

        # Parse response
        response_text = response.content[0].text
        logger.debug(f"Claude response: {response_text[:200]}...")

        # Try to parse JSON response
        import json
        import re
        try:
            # Clean up response text
            cleaned_text = response_text.strip()

            # Extract JSON from markdown code blocks if present
            if "```json" in cleaned_text:
                json_start = cleaned_text.find("```json") + 7
                json_end = cleaned_text.find("```", json_start)
                cleaned_text = cleaned_text[json_start:json_end].strip()
            elif "```" in cleaned_text:
                json_start = cleaned_text.find("```") + 3
                json_end = cleaned_text.find("```", json_start)
                cleaned_text = cleaned_text[json_start:json_end].strip()

            # Try to find JSON object in text
            if not cleaned_text.startswith("{"):
                match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
                if match:
                    cleaned_text = match.group()

            result = json.loads(cleaned_text)
            logger.info(f"✅ Analysis complete: {result.get('analysis', '')[:100]}...")

            # Validate coordinates if present
            if "recommended_action" in result and result["recommended_action"]:
                action = result["recommended_action"]
                if "coordinates" in action:
                    coords = action["coordinates"]
                    x = coords.get("x", 0.5)
                    y = coords.get("y", 0.5)

                    # Ensure coordinates are floats between 0 and 1
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        # If values > 1, they might be pixels - convert to percentage
                        if x > 1 or y > 1:
                            screen_w, screen_h = pyautogui.size()
                            logger.warning(f"Coordinates appear to be pixels, converting: ({x}, {y})")
                            coords["x"] = x / screen_w if x > 1 else x
                            coords["y"] = y / screen_h if y > 1 else y
                            logger.info(f"Converted to percentages: ({coords['x']:.3f}, {coords['y']:.3f})")

            return result

        except json.JSONDecodeError as e:
            # Fallback to text response
            logger.warning(f"Could not parse JSON ({e}), using text response")
            logger.debug(f"Response text: {response_text[:500]}")
            return {
                "analysis": response_text,
                "ui_elements": [],
                "recommended_action": None,
                "confidence": 0.5
            }

    def execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Execute a computer action (click, type, etc.)

        Args:
            action: Action dict with type, coordinates, value

        Returns:
            True if successful
        """
        action_type = action.get("type")

        try:
            if action_type == "click":
                coords = action.get("coordinates", {})
                x_val = coords.get("x", 0.5)
                y_val = coords.get("y", 0.5)

                # Convert to pixel coordinates
                screen_w, screen_h = pyautogui.size()

                # Check if values are percentages (0-1) or pixel coordinates
                if isinstance(x_val, float) and x_val <= 1.0 and isinstance(y_val, float) and y_val <= 1.0:
                    # Percentage coordinates
                    x = int(screen_w * x_val)
                    y = int(screen_h * y_val)
                    logger.debug(f"Using percentage coords: {x_val:.2f}, {y_val:.2f} -> ({x}, {y})")
                else:
                    # Pixel coordinates
                    x = int(x_val)
                    y = int(y_val)
                    logger.debug(f"Using pixel coords: ({x}, {y})")

                logger.info(f"🖱️  Clicking at ({x}, {y})")

                # Move to position first, then click (more reliable)
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(0.2)
                pyautogui.click()

                return True

            elif action_type == "type":
                text = action.get("value", "")
                logger.info(f"⌨️  Typing: {text}")
                pyautogui.write(text, interval=0.1)
                return True

            elif action_type == "key":
                key = action.get("value", "")
                logger.info(f"⌨️  Pressing key: {key}")
                pyautogui.press(key)
                return True

            elif action_type == "wait":
                duration = action.get("value", 1)
                logger.info(f"⏱️  Waiting {duration}s")
                time.sleep(duration)
                return True

            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False

        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return False

    def automate_task(self, task_description: str, max_iterations: int = 5) -> bool:
        """
        Automatically complete a task by analyzing screen and taking actions

        Args:
            task_description: Natural language task description
            max_iterations: Maximum number of analyze-act cycles

        Returns:
            True if task completed successfully
        """
        logger.info(f"🎯 Starting automated task: {task_description}")

        for iteration in range(max_iterations):
            logger.info(f"Iteration {iteration + 1}/{max_iterations}")

            # Capture and analyze screen
            analysis = self.analyze_screen(task_description)

            # Check if task is complete
            if "complete" in analysis.get("analysis", "").lower():
                logger.success("✅ Task completed!")
                return True

            # Get recommended action
            action = analysis.get("recommended_action")

            if not action:
                logger.warning("No action recommended, task may be complete")
                return True

            # Execute action
            success = self.execute_action(action)

            if not success:
                logger.error("Failed to execute action")
                return False

            # Wait a bit for UI to update
            time.sleep(1)

        logger.warning(f"Task not completed after {max_iterations} iterations")
        return False

    def click_on_text(self, text: str, confidence: float = 0.8) -> bool:
        """
        Find and click on specific text on screen

        Args:
            text: Text to find and click
            confidence: Confidence threshold for OCR

        Returns:
            True if clicked
        """
        logger.info(f"🔍 Looking for text: '{text}'")

        # Take screenshot and analyze
        analysis = self.analyze_screen(f"Find and click on the text '{text}'")

        action = analysis.get("recommended_action")
        if action and action.get("type") == "click":
            return self.execute_action(action)

        logger.warning(f"Could not find text: '{text}'")
        return False

    def handle_dialog(self, expected_buttons: Optional[List[str]] = None) -> bool:
        """
        Detect and handle a dialog by clicking appropriate button

        Args:
            expected_buttons: List of button texts to look for (e.g., ["Yes", "OK"])

        Returns:
            True if dialog handled
        """
        logger.info("🔍 Looking for dialog...")

        buttons_text = ", ".join(expected_buttons) if expected_buttons else "Yes, OK, Allow, Continue"

        analysis = self.analyze_screen(
            f"Is there a dialog on screen? If yes, click on one of these buttons: {buttons_text}"
        )

        action = analysis.get("recommended_action")
        if action:
            return self.execute_action(action)

        logger.info("No dialog detected")
        return False


# Global instance
computer_use_agent = None

def get_computer_use_agent() -> ComputerUseAgent:
    """Get or create global computer use agent"""
    global computer_use_agent

    if computer_use_agent is None:
        computer_use_agent = ComputerUseAgent()

    return computer_use_agent
