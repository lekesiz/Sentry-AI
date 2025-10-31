"""
LLM Response Parser for Sentry-AI.

This module provides robust parsing for LLM responses,
handling various response formats and edge cases.
"""

import re
from typing import List, Dict, Optional
from loguru import logger


def parse_structured_response(
    response: str,
    options: List[str],
    confidence: float = 0.8
) -> Dict[str, any]:
    """
    Parse a structured response from an LLM.
    
    Handles various response formats:
    - "1" or "1." or "1)" 
    - "Save" (direct option name)
    - "1. Save - because..."
    - "I choose option 2"
    - etc.
    
    Args:
        response: Raw LLM response text
        options: List of available options
        confidence: Default confidence score
        
    Returns:
        Dictionary with 'choice', 'reasoning', and 'confidence' keys
    """
    response = response.strip()
    lines = response.split('\n')
    first_line = lines[0].strip()
    
    # Try different parsing strategies
    choice = None
    reasoning = ""
    
    # Strategy 1: Look for a number at the start
    number_match = re.match(r'^(\d+)[.):\s-]*', first_line)
    if number_match:
        try:
            choice_num = int(number_match.group(1))
            if 1 <= choice_num <= len(options):
                choice = options[choice_num - 1]
                # Extract reasoning from the rest
                reasoning_start = number_match.end()
                reasoning = first_line[reasoning_start:].strip()
                if len(lines) > 1:
                    reasoning += " " + " ".join(lines[1:])
                logger.debug(f"Parsed choice by number: {choice}")
        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse number: {e}")
    
    # Strategy 2: Look for option name directly in response
    if not choice:
        response_lower = response.lower()
        for i, option in enumerate(options):
            if option.lower() in response_lower:
                choice = option
                # Try to extract reasoning
                parts = response.split(option, 1)
                if len(parts) > 1:
                    reasoning = parts[1].strip()
                logger.debug(f"Parsed choice by name match: {choice}")
                break
    
    # Strategy 3: Look for "option X" or "choice X" pattern
    if not choice:
        option_match = re.search(r'(?:option|choice)\s+(\d+)', response_lower)
        if option_match:
            try:
                choice_num = int(option_match.group(1))
                if 1 <= choice_num <= len(options):
                    choice = options[choice_num - 1]
                    logger.debug(f"Parsed choice by 'option X' pattern: {choice}")
            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse 'option X' pattern: {e}")
    
    # Strategy 4: Fuzzy match - find closest option
    if not choice:
        response_words = set(response_lower.split())
        best_match = None
        best_score = 0
        
        for option in options:
            option_words = set(option.lower().split())
            # Calculate word overlap
            overlap = len(response_words & option_words)
            if overlap > best_score:
                best_score = overlap
                best_match = option
        
        if best_match and best_score > 0:
            choice = best_match
            reasoning = "Fuzzy matched based on word overlap"
            logger.debug(f"Parsed choice by fuzzy match: {choice}")
    
    # Fallback: Use first option
    if not choice:
        choice = options[0]
        reasoning = "Fallback to first option - could not parse response"
        confidence = 0.3
        logger.warning(f"Could not parse LLM response, using fallback. Response: {response[:100]}")
    
    # Clean up reasoning
    if not reasoning:
        reasoning = "No explicit reasoning provided"
    reasoning = reasoning.strip()
    
    return {
        "choice": choice,
        "reasoning": reasoning,
        "confidence": confidence
    }


def extract_button_names(elements: List[any]) -> List[str]:
    """
    Extract button names from UI elements.
    
    Args:
        elements: List of UIElement objects
        
    Returns:
        List of button names/titles
    """
    buttons = []
    for element in elements:
        if hasattr(element, 'role') and element.role == "AXButton":
            if hasattr(element, 'title') and element.title:
                buttons.append(element.title)
    return buttons
