"""
OCR Helper for Sentry-AI using Apple Vision Framework.

This module provides OCR functionality as a fallback when the Accessibility API
cannot extract text from UI elements (e.g., for non-native apps).
"""

import os
from typing import Optional, List, Tuple
from pathlib import Path
from loguru import logger

try:
    from Foundation import NSURL
    from Vision import (
        VNRecognizeTextRequest,
        VNImageRequestHandler,
        VNRequestTextRecognitionLevelAccurate,
    )
    from Quartz import CGImageSourceCreateWithURL, CGImageSourceCreateImageAtIndex
    VISION_AVAILABLE = True
except ImportError:
    logger.warning("Apple Vision Framework not available. OCR will not work.")
    VISION_AVAILABLE = False


class OCRHelper:
    """Helper class for OCR operations using Apple Vision Framework."""
    
    def __init__(self):
        """Initialize the OCR helper."""
        self.available = VISION_AVAILABLE
        
        if not self.available:
            logger.warning("OCR functionality is disabled (Vision Framework not available)")
    
    def extract_text_from_image(
        self, 
        image_path: str,
        recognition_level: str = "accurate"
    ) -> Optional[List[Tuple[str, float]]]:
        """
        Extract text from an image using Vision Framework OCR.
        
        Args:
            image_path: Path to the image file
            recognition_level: "accurate" or "fast" (default: accurate)
            
        Returns:
            List of tuples (text, confidence) or None if extraction fails
        """
        if not self.available:
            logger.error("OCR not available - Vision Framework not loaded")
            return None
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None
        
        try:
            # Create NSURL from file path
            url = NSURL.fileURLWithPath_(image_path)
            
            # Create image source
            image_source = CGImageSourceCreateWithURL(url, None)
            if not image_source:
                logger.error(f"Failed to create image source from {image_path}")
                return None
            
            # Get the image
            image = CGImageSourceCreateImageAtIndex(image_source, 0, None)
            if not image:
                logger.error(f"Failed to extract image from source")
                return None
            
            # Create text recognition request
            request = VNRecognizeTextRequest.alloc().init()
            
            # Set recognition level
            if recognition_level == "accurate":
                request.setRecognitionLevel_(VNRequestTextRecognitionLevelAccurate)
            
            # Create request handler
            handler = VNImageRequestHandler.alloc().initWithCGImage_options_(image, None)
            
            # Perform the request
            success = handler.performRequests_error_([request], None)
            
            if not success:
                logger.error("OCR request failed")
                return None
            
            # Extract results
            results = request.results()
            if not results:
                logger.warning("No text found in image")
                return []
            
            # Parse results
            extracted_texts = []
            for observation in results:
                text = observation.topCandidates_(1)[0].string()
                confidence = observation.confidence()
                extracted_texts.append((text, confidence))
            
            logger.info(f"Extracted {len(extracted_texts)} text blocks from image")
            return extracted_texts
        
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return None
    
    def extract_text_from_screen_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: Optional[str] = None
    ) -> Optional[List[Tuple[str, float]]]:
        """
        Capture a screen region and extract text from it.
        
        Args:
            x: X coordinate of the region
            y: Y coordinate of the region
            width: Width of the region
            height: Height of the region
            output_path: Optional path to save the screenshot
            
        Returns:
            List of tuples (text, confidence) or None if extraction fails
        """
        if not self.available:
            logger.error("OCR not available - Vision Framework not loaded")
            return None
        
        try:
            # Import screenshot utility
            from .screenshot_helper import capture_screen_region
            
            # Capture the screen region
            if output_path is None:
                output_path = f"/tmp/sentry_ai_ocr_{os.getpid()}.png"
            
            success = capture_screen_region(x, y, width, height, output_path)
            
            if not success:
                logger.error("Failed to capture screen region")
                return None
            
            # Extract text from the captured image
            return self.extract_text_from_image(output_path)
        
        except Exception as e:
            logger.error(f"Error capturing and processing screen region: {e}")
            return None
    
    def find_text_in_image(
        self,
        image_path: str,
        search_text: str,
        case_sensitive: bool = False
    ) -> bool:
        """
        Check if specific text exists in an image.
        
        Args:
            image_path: Path to the image file
            search_text: Text to search for
            case_sensitive: Whether the search should be case-sensitive
            
        Returns:
            True if text is found, False otherwise
        """
        extracted = self.extract_text_from_image(image_path)
        
        if not extracted:
            return False
        
        # Combine all extracted text
        all_text = " ".join([text for text, _ in extracted])
        
        if case_sensitive:
            return search_text in all_text
        else:
            return search_text.lower() in all_text.lower()


# Global instance
ocr_helper = OCRHelper()
