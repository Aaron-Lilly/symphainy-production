#!/usr/bin/env python3
"""
OpenCV Image Processing Infrastructure Adapter - Layer 1

Raw technology wrapper for image processing using OpenCV.
This is a very specific, focused adapter for image enhancement operations.

WHAT (Infrastructure): I provide image processing capabilities
HOW (Adapter): I wrap OpenCV library for image enhancement
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
import os
import tempfile

# Dependency Injection for standard libraries
# OpenCV adapter requires numpy - fail gracefully if not available
MISSING_DEPENDENCIES = None
try:
    import cv2
    import numpy as np
    from PIL import Image
    NDArray = np.ndarray  # Type alias for when numpy is available
    CV2_AVAILABLE = True
    NUMPY_AVAILABLE = True
    PIL_AVAILABLE = True
except ImportError as e:
    # Required dependencies not available - adapter cannot function
    CV2_AVAILABLE = False
    NUMPY_AVAILABLE = False
    PIL_AVAILABLE = False
    cv2 = None
    np = None
    Image = None
    NDArray = Any  # Fallback type when numpy is not available
    MISSING_DEPENDENCIES = str(e)

logger = logging.getLogger(__name__)

class OpenCVImageProcessor:
    """
    OpenCV Image Processing Infrastructure Adapter
    
    Raw technology wrapper for image processing using OpenCV.
    Provides basic image enhancement functionality without business logic.
    """
    
    def __init__(self):
        """Initialize OpenCV Image Processor."""
        self.logger = logging.getLogger("OpenCVImageProcessor")
        self.cv2_available = CV2_AVAILABLE
        self.np_available = NUMPY_AVAILABLE
        self.pil_available = PIL_AVAILABLE
        
        # OpenCV adapter requires numpy and cv2 - fail gracefully if not available
        if not self.np_available:
            error_msg = (
                "OpenCVImageProcessor requires numpy but it is not installed. "
                f"Install with: pip install numpy opencv-python pillow. "
                f"Original error: {MISSING_DEPENDENCIES if MISSING_DEPENDENCIES else 'ImportError'}"
            )
            self.logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        if not self.cv2_available:
            error_msg = (
                "OpenCVImageProcessor requires opencv-python but it is not installed. "
                f"Install with: pip install opencv-python. "
                f"Original error: {MISSING_DEPENDENCIES if MISSING_DEPENDENCIES else 'ImportError'}"
            )
            self.logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        if not self.pil_available:
            self.logger.warning("⚠️ 'PIL' library not found. Image loading functionality will be limited.")
        
        self.logger.info("✅ OpenCV Image Processor initialized")
    
    async def enhance_image(self, image_path: str, enhancement_type: str = "standard") -> Dict[str, Any]:
        """
        Enhance image for better OCR results.
        
        Args:
            image_path: Path to input image
            enhancement_type: Type of enhancement (standard, aggressive, gentle)
            
        Returns:
            Dict containing enhanced image path and metadata
        """
        try:
            if not self.cv2_available or not self.np_available:
                return {
                    "success": False,
                    "error": "Required image processing libraries not available",
                    "enhanced_path": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": "Could not load image",
                    "enhanced_path": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Apply enhancement based on type
            if enhancement_type == "aggressive":
                enhanced = self._apply_aggressive_enhancement(image)
            elif enhancement_type == "gentle":
                enhanced = self._apply_gentle_enhancement(image)
            else:  # standard
                enhanced = self._apply_standard_enhancement(image)
            
            # Save enhanced image
            enhanced_path = self._save_enhanced_image(enhanced, image_path)
            
            return {
                "success": True,
                "enhanced_path": enhanced_path,
                "enhancement_type": enhancement_type,
                "original_size": image.shape,
                "enhanced_size": enhanced.shape,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Image enhancement failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "enhanced_path": None,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _apply_standard_enhancement(self, image: NDArray) -> NDArray:
        """Apply standard image enhancement."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply contrast enhancement
            enhanced = cv2.convertScaleAbs(gray, alpha=1.2, beta=10)
            
            # Apply noise reduction
            enhanced = cv2.medianBlur(enhanced, 3)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"❌ Standard enhancement failed: {e}")
            return image
    
    def _apply_aggressive_enhancement(self, image: NDArray) -> NDArray:
        """Apply aggressive image enhancement."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply strong contrast enhancement
            enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=20)
            
            # Apply morphological operations
            kernel = np.ones((2, 2), np.uint8)
            enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
            
            # Apply adaptive thresholding
            enhanced = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"❌ Aggressive enhancement failed: {e}")
            return image
    
    def _apply_gentle_enhancement(self, image: NDArray) -> NDArray:
        """Apply gentle image enhancement."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply mild contrast enhancement
            enhanced = cv2.convertScaleAbs(gray, alpha=1.1, beta=5)
            
            # Apply gentle noise reduction
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"❌ Gentle enhancement failed: {e}")
            return image
    
    def _save_enhanced_image(self, enhanced_image: NDArray, original_path: str) -> str:
        """Save enhanced image to temporary file."""
        try:
            # Create temporary file
            temp_dir = os.path.dirname(original_path)
            temp_file = tempfile.NamedTemporaryFile(
                suffix='_enhanced.jpg', 
                dir=temp_dir, 
                delete=False
            )
            temp_path = temp_file.name
            temp_file.close()
            
            # Save enhanced image
            cv2.imwrite(temp_path, enhanced_image)
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save enhanced image: {e}")
            return None
    
    async def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get image information and metadata.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing image information
        """
        try:
            if not self.cv2_available:
                return {
                    "success": False,
                    "error": "OpenCV not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": "Could not load image",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Get image properties
            height, width, channels = image.shape
            file_size = os.path.getsize(image_path)
            
            return {
                "success": True,
                "dimensions": {
                    "width": width,
                    "height": height,
                    "channels": channels
                },
                "file_size": file_size,
                "aspect_ratio": width / height if height > 0 else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get image info: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def detect_text_regions(self, image_path: str) -> Dict[str, Any]:
        """
        Detect text regions in image using OpenCV.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing detected text regions
        """
        try:
            if not self.cv2_available:
                return {
                    "success": False,
                    "error": "OpenCV not available",
                    "regions": [],
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": "Could not load image",
                    "regions": [],
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours that might be text
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # Filter based on size and aspect ratio
                if area > 100 and w > 10 and h > 10:
                    aspect_ratio = w / h
                    if 0.1 < aspect_ratio < 10:  # Reasonable text aspect ratio
                        text_regions.append({
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "area": area,
                            "aspect_ratio": aspect_ratio
                        })
            
            return {
                "success": True,
                "regions": text_regions,
                "region_count": len(text_regions),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Text region detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "regions": [],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get adapter capabilities."""
        return {
            "adapter_name": "OpenCVImageProcessor",
            "status": "ready" if self.cv2_available else "unavailable",
            "libraries": {
                "cv2": self.cv2_available,
                "numpy": self.np_available,
                "pil": self.pil_available
            },
            "capabilities": [
                "image_enhancement",
                "noise_reduction",
                "contrast_enhancement",
                "text_region_detection",
                "morphological_operations"
            ],
            "enhancement_types": ["standard", "aggressive", "gentle"],
            "timestamp": datetime.utcnow().isoformat()
        }






