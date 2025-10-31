"""
Screenshot Helper for Sentry-AI.

This module provides screenshot functionality for capturing screen regions,
which can then be processed by the OCR helper.
"""

import os
from typing import Optional
from loguru import logger

try:
    from Quartz import (
        CGWindowListCreateImage,
        CGRectMake,
        CGRectInfinite,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
    )
    from Quartz.CoreGraphics import (
        CGImageGetWidth,
        CGImageGetHeight,
    )
    from Foundation import NSURL
    from AppKit import NSBitmapImageRep, NSPNGFileType
    QUARTZ_AVAILABLE = True
except ImportError:
    logger.warning("Quartz framework not available. Screenshot functionality disabled.")
    QUARTZ_AVAILABLE = False


def capture_screen_region(
    x: int,
    y: int,
    width: int,
    height: int,
    output_path: str
) -> bool:
    """
    Capture a specific region of the screen and save it as PNG.
    
    Args:
        x: X coordinate of the top-left corner
        y: Y coordinate of the top-left corner
        width: Width of the region to capture
        height: Height of the region to capture
        output_path: Path where to save the screenshot
        
    Returns:
        True if successful, False otherwise
    """
    if not QUARTZ_AVAILABLE:
        logger.error("Screenshot not available - Quartz framework not loaded")
        return False
    
    try:
        # Create the rectangle for the region
        rect = CGRectMake(x, y, width, height)
        
        # Capture the screen region
        image = CGWindowListCreateImage(
            rect,
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID,
            0
        )
        
        if not image:
            logger.error("Failed to capture screen region")
            return False
        
        # Create bitmap representation
        bitmap = NSBitmapImageRep.alloc().initWithCGImage_(image)
        
        # Convert to PNG data
        png_data = bitmap.representationUsingType_properties_(
            NSPNGFileType,
            None
        )
        
        # Write to file
        png_data.writeToFile_atomically_(output_path, True)
        
        logger.debug(f"Screenshot saved to {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error capturing screen region: {e}")
        return False


def capture_full_screen(output_path: str) -> bool:
    """
    Capture the entire screen and save it as PNG.
    
    Args:
        output_path: Path where to save the screenshot
        
    Returns:
        True if successful, False otherwise
    """
    if not QUARTZ_AVAILABLE:
        logger.error("Screenshot not available - Quartz framework not loaded")
        return False
    
    try:
        # Capture the entire screen
        image = CGWindowListCreateImage(
            CGRectInfinite,
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID,
            0
        )
        
        if not image:
            logger.error("Failed to capture full screen")
            return False
        
        # Create bitmap representation
        bitmap = NSBitmapImageRep.alloc().initWithCGImage_(image)
        
        # Convert to PNG data
        png_data = bitmap.representationUsingType_properties_(
            NSPNGFileType,
            None
        )
        
        # Write to file
        png_data.writeToFile_atomically_(output_path, True)
        
        width = CGImageGetWidth(image)
        height = CGImageGetHeight(image)
        
        logger.info(f"Full screen captured ({width}x{height}) to {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error capturing full screen: {e}")
        return False


def capture_window(window_id: int, output_path: str) -> bool:
    """
    Capture a specific window and save it as PNG.
    
    Args:
        window_id: The window ID to capture
        output_path: Path where to save the screenshot
        
    Returns:
        True if successful, False otherwise
    """
    if not QUARTZ_AVAILABLE:
        logger.error("Screenshot not available - Quartz framework not loaded")
        return False
    
    try:
        # Capture the specific window
        image = CGWindowListCreateImage(
            CGRectInfinite,
            kCGWindowListOptionOnScreenOnly,
            window_id,
            0
        )
        
        if not image:
            logger.error(f"Failed to capture window {window_id}")
            return False
        
        # Create bitmap representation
        bitmap = NSBitmapImageRep.alloc().initWithCGImage_(image)
        
        # Convert to PNG data
        png_data = bitmap.representationUsingType_properties_(
            NSPNGFileType,
            None
        )
        
        # Write to file
        png_data.writeToFile_atomically_(output_path, True)
        
        logger.debug(f"Window {window_id} captured to {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error capturing window: {e}")
        return False
