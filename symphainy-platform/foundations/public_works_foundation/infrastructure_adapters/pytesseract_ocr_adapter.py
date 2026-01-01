#!/usr/bin/env python3
"""
PyTesseract OCR Infrastructure Adapter - Layer 1

Raw technology wrapper for OCR text extraction using PyTesseract.
This is a very specific, focused adapter for OCR operations.

WHAT (Infrastructure): I provide OCR text extraction capabilities
HOW (Adapter): I wrap PyTesseract library for text extraction
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import tempfile
import io

# Dependency Injection for standard libraries
# PyTesseract adapter requires dependencies - fail gracefully if not available
MISSING_DEPENDENCIES = None
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    PYTESSERACT_AVAILABLE = True
    PIL_AVAILABLE = True
    CV2_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError as e:
    # Required dependencies not available - adapter cannot function
    PYTESSERACT_AVAILABLE = False
    PIL_AVAILABLE = False
    CV2_AVAILABLE = False
    NUMPY_AVAILABLE = False
    pytesseract = None
    Image = None
    cv2 = None
    np = None
    MISSING_DEPENDENCIES = str(e)

logger = logging.getLogger(__name__)

class PyTesseractOCRAdapter:
    """
    PyTesseract OCR Infrastructure Adapter
    
    Raw technology wrapper for OCR text extraction using PyTesseract.
    Provides basic OCR functionality without business logic.
    """
    
    def __init__(self):
        """Initialize PyTesseract OCR Adapter."""
        self.logger = logging.getLogger("PyTesseractOCRAdapter")
        self.pytesseract_available = PYTESSERACT_AVAILABLE
        self.pil_available = PIL_AVAILABLE
        self.cv2_available = CV2_AVAILABLE
        self.np_available = NUMPY_AVAILABLE
        
        # PyTesseract adapter requires pytesseract and numpy - fail gracefully if not available
        if not self.pytesseract_available:
            error_msg = (
                "PyTesseractOCRAdapter requires pytesseract but it is not installed. "
                f"Install with: pip install pytesseract. "
                f"Also ensure Tesseract OCR is installed on your system. "
                f"Original error: {MISSING_DEPENDENCIES if MISSING_DEPENDENCIES else 'ImportError'}"
            )
            self.logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        if not self.np_available:
            error_msg = (
                "PyTesseractOCRAdapter requires numpy but it is not installed. "
                f"Install with: pip install numpy. "
                f"Original error: {MISSING_DEPENDENCIES if MISSING_DEPENDENCIES else 'ImportError'}"
            )
            self.logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        if not self.pil_available:
            self.logger.warning("⚠️ 'PIL' library not found. Image processing functionality will be limited.")
        if not self.cv2_available:
            self.logger.warning("⚠️ 'cv2' library not found. Image enhancement functionality will be limited.")
        
        self.logger.info("✅ PyTesseract OCR Adapter initialized")
    
    async def extract_text(self, image_path: str, language: str = "eng", 
                          config: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract text from image using PyTesseract.
        
        Args:
            image_path: Path to image file
            language: OCR language (default: eng)
            config: Tesseract configuration string
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            if not self.pytesseract_available or not self.pil_available:
                return {
                    "success": False,
                    "error": "Required OCR libraries not available",
                    "text": "",
                    "confidence": 0.0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Load image
            image = Image.open(image_path)
            
            # Perform OCR
            if config:
                text = pytesseract.image_to_string(image, lang=language, config=config)
            else:
                text = pytesseract.image_to_string(image, lang=language)
            
            # Get confidence data
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "success": True,
                "text": text.strip(),
                "confidence": avg_confidence / 100.0,  # Convert to 0-1 scale
                "language": language,
                "word_count": len(text.split()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ OCR text extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_text_from_bytes(self, image_data: bytes, language: str = "eng", 
                                      config: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract text from image bytes using PyTesseract.
        
        Args:
            image_data: Image file content as bytes
            language: OCR language (default: eng)
            config: Tesseract configuration string
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            if not self.pytesseract_available or not self.pil_available:
                return {
                    "success": False,
                    "error": "Required OCR libraries not available",
                    "text": "",
                    "confidence": 0.0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Perform OCR
            if config:
                text = pytesseract.image_to_string(image, lang=language, config=config)
            else:
                text = pytesseract.image_to_string(image, lang=language)
            
            # Get confidence data
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "success": True,
                "text": text.strip(),
                "confidence": avg_confidence / 100.0,  # Convert to 0-1 scale
                "language": language,
                "word_count": len(text.split()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ OCR text extraction from bytes failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_text_with_boxes(self, image_path: str, language: str = "eng") -> Dict[str, Any]:
        """
        Extract text with bounding boxes using PyTesseract.
        
        Args:
            image_path: Path to image file
            language: OCR language (default: eng)
            
        Returns:
            Dict containing text, boxes, and metadata
        """
        try:
            if not self.pytesseract_available or not self.pil_available:
                return {
                    "success": False,
                    "error": "Required OCR libraries not available",
                    "text": "",
                    "boxes": [],
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Load image
            image = Image.open(image_path)
            
            # Get bounding box data
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Extract text and boxes
            text_boxes = []
            full_text = ""
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Only include text with confidence > 0
                    text = data['text'][i].strip()
                    if text:
                        box = {
                            "text": text,
                            "confidence": int(data['conf'][i]) / 100.0,
                            "bbox": {
                                "left": int(data['left'][i]),
                                "top": int(data['top'][i]),
                                "width": int(data['width'][i]),
                                "height": int(data['height'][i])
                            }
                        }
                        text_boxes.append(box)
                        full_text += text + " "
            
            return {
                "success": True,
                "text": full_text.strip(),
                "boxes": text_boxes,
                "box_count": len(text_boxes),
                "language": language,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ OCR text extraction with boxes failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "boxes": [],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported OCR languages."""
        try:
            if not self.pytesseract_available:
                return {
                    "success": False,
                    "error": "PyTesseract not available",
                    "languages": [],
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Get available languages
            languages = pytesseract.get_languages()
            
            return {
                "success": True,
                "languages": languages,
                "language_count": len(languages),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get supported languages: {e}")
            return {
                "success": False,
                "error": str(e),
                "languages": [],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get adapter capabilities."""
        return {
            "adapter_name": "PyTesseractOCRAdapter",
            "status": "ready" if self.pytesseract_available else "unavailable",
            "libraries": {
                "pytesseract": self.pytesseract_available,
                "pil": self.pil_available,
                "cv2": self.cv2_available
            },
            "capabilities": [
                "text_extraction",
                "confidence_scoring",
                "bounding_boxes",
                "multi_language"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }






