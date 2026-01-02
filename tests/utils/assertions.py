"""
Custom assertions for test validation.

Provides domain-specific assertions for SymphAIny Platform testing.
"""

from typing import Any, Dict, List, Optional
import re


def assert_health_check_response(response: Dict[str, Any]):
    """
    Assert that a health check response is valid.
    
    Args:
        response: Health check response dictionary
    """
    assert "status" in response, "Health check response missing 'status' field"
    assert response["status"] in ["healthy", "unhealthy", "degraded"], \
        f"Invalid health status: {response['status']}"
    
    if response["status"] == "healthy":
        assert "timestamp" in response, "Healthy response missing 'timestamp'"


def assert_api_response(response: Dict[str, Any], expected_status: str = "success"):
    """
    Assert that an API response has the expected structure.
    
    Args:
        response: API response dictionary
        expected_status: Expected status value
    """
    assert "status" in response or "success" in response, \
        "API response missing status/success field"
    
    status = response.get("status") or response.get("success")
    assert status == expected_status, \
        f"Expected status '{expected_status}', got '{status}'"


def assert_no_placeholders_in_response(response: Any, path: str = ""):
    """
    Assert that an API response contains no placeholder values.
    
    Args:
        response: API response (dict, list, str, etc.)
        path: Current path in nested structure
    """
    placeholder_patterns = [
        r"placeholder",
        r"TODO",
        r"FIXME",
        r"XXX",
        r"TBD",
        r"mock",
        r"stub",
        r"example\.com",
        r"test@test\.com",
    ]
    
    if isinstance(response, dict):
        for key, value in response.items():
            full_path = f"{path}.{key}" if path else key
            assert_no_placeholders_in_response(value, full_path)
    elif isinstance(response, list):
        for i, item in enumerate(response):
            full_path = f"{path}[{i}]" if path else f"[{i}]"
            assert_no_placeholders_in_response(item, full_path)
    elif isinstance(response, str):
        response_lower = response.lower()
        for pattern in placeholder_patterns:
            if re.search(pattern, response_lower, re.IGNORECASE):
                raise AssertionError(
                    f"Found placeholder pattern '{pattern}' at {path}: {response[:100]}"
                )


def assert_pillar_response(response: Dict[str, Any], pillar_name: str):
    """
    Assert that a pillar response has the expected structure.
    
    Args:
        response: Pillar response dictionary
        pillar_name: Name of pillar (content, insights, operations, business_outcomes)
    """
    assert "status" in response or "success" in response, \
        f"{pillar_name} pillar response missing status/success"
    
    # Pillar-specific validations
    if pillar_name == "content":
        assert "file_id" in response or "parsed_file_id" in response, \
            "Content pillar response missing file identifiers"
    elif pillar_name == "insights":
        assert "analysis" in response or "insights" in response, \
            "Insights pillar response missing analysis/insights"
    elif pillar_name == "operations":
        assert "workflow" in response or "sop" in response or "blueprint" in response, \
            "Operations pillar response missing workflow/sop/blueprint"
    elif pillar_name == "business_outcomes":
        assert "roadmap" in response or "poc" in response or "summary" in response, \
            "Business Outcomes pillar response missing roadmap/poc/summary"


def assert_websocket_message(message: Dict[str, Any], expected_type: Optional[str] = None):
    """
    Assert that a WebSocket message has the expected structure.
    
    Args:
        message: WebSocket message dictionary
        expected_type: Expected message type (optional)
    """
    assert "type" in message or "event" in message, \
        "WebSocket message missing type/event field"
    
    if expected_type:
        msg_type = message.get("type") or message.get("event")
        assert msg_type == expected_type, \
            f"Expected message type '{expected_type}', got '{msg_type}'"


def assert_saga_state(saga_state: Dict[str, Any], expected_status: Optional[str] = None):
    """
    Assert that a Saga state has the expected structure.
    
    Args:
        saga_state: Saga state dictionary
        expected_status: Expected saga status (optional)
    """
    assert "saga_id" in saga_state, "Saga state missing saga_id"
    assert "status" in saga_state, "Saga state missing status"
    
    valid_statuses = ["pending", "in_progress", "completed", "compensated", "failed"]
    assert saga_state["status"] in valid_statuses, \
        f"Invalid saga status: {saga_state['status']}"
    
    if expected_status:
        assert saga_state["status"] == expected_status, \
            f"Expected saga status '{expected_status}', got '{saga_state['status']}'"




