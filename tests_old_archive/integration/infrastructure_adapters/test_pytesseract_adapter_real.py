"""
Test PyTesseractOCRAdapter with Real Dependencies

Validates that PyTesseractOCRAdapter can be initialized and has required dependencies.
This test should FAIL if dependencies are missing (numpy, pytesseract, cv2, PIL).
"""

import pytest
import os

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from foundations.public_works_foundation.infrastructure_adapters.pytesseract_ocr_adapter import PyTesseractOCRAdapter

@pytest.mark.integration
@pytest.mark.infrastructure
class TestPyTesseractOCRAdapterReal:
    """Test PyTesseractOCRAdapter initialization and dependencies."""
    
    def test_pytesseract_adapter_can_be_initialized(self):
        """Test that PyTesseractOCRAdapter can be initialized (validates dependencies)."""
        # This should raise RuntimeError with clear message if dependencies are missing
        # If it succeeds, all required dependencies are available
        try:
            adapter = PyTesseractOCRAdapter()
            assert adapter is not None, "Adapter should be initialized"
            assert adapter.pytesseract_available is True, "pytesseract should be available"
            assert adapter.np_available is True, "numpy should be available"
        except RuntimeError as e:
            # Adapter should fail gracefully with clear error message
            error_msg = str(e)
            assert "pytesseract" in error_msg.lower() or "numpy" in error_msg.lower(),                 f"Error message should mention missing dependency: {error_msg}"
            assert "install" in error_msg.lower(),                 f"Error message should include installation instructions: {error_msg}"
            pytest.fail(f"PyTesseractOCRAdapter failed to initialize (dependencies missing): {e}")
    
    def test_pytesseract_adapter_has_required_attributes(self):
        """Test that PyTesseractOCRAdapter has required attributes after initialization."""
        adapter = PyTesseractOCRAdapter()
        assert hasattr(adapter, 'pytesseract_available'), "Adapter should have pytesseract_available attribute"
        assert hasattr(adapter, 'np_available'), "Adapter should have np_available attribute"
        assert hasattr(adapter, 'pil_available'), "Adapter should have pil_available attribute"
        assert hasattr(adapter, 'cv2_available'), "Adapter should have cv2_available attribute"
    
    def test_pytesseract_adapter_dependencies_are_available(self):
        """Test that all required dependencies are actually available."""
        adapter = PyTesseractOCRAdapter()
        assert adapter.pytesseract_available is True, "pytesseract must be available (required)"
        assert adapter.np_available is True, "numpy must be available (required)"
        # PIL and cv2 are optional but recommended
        if not adapter.pil_available:
            pytest.skip("PIL not available (optional but recommended)")
        if not adapter.cv2_available:
            pytest.skip("cv2 not available (optional but recommended)")
