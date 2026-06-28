"""
Velour API — AI Gateway tests.
"""

from unittest.mock import patch, MagicMock
import pytest

from app.ai.gateway import AIGateway, InferenceError


class MockAdapter:
    """A dummy adapter for testing retries."""
    
    def __init__(self):
        self.call_count = 0

    def succeed_fast(self):
        return "success"
        
    def fail_always(self):
        raise ValueError("Simulated crash inside model")
        
    def succeed_on_third_try(self):
        # We need a shared state across instances since tenacity recreates the class
        global mock_call_count
        mock_call_count += 1
        if mock_call_count < 3:
            raise RuntimeError("Temporary GPU out of memory")
        return "finally success"


mock_call_count = 0


def test_gateway_success():
    """Test standard success without retries."""
    gateway = AIGateway()
    result = gateway.execute_adapter(MockAdapter, "succeed_fast")
    assert result == "success"


def test_gateway_retry_failure():
    """Test that it retries and eventually raises InferenceError."""
    gateway = AIGateway()
    
    with pytest.raises(InferenceError, match="Adapter failed: Simulated crash inside model"):
        # We wrap wait_exponential so tests run instantly
        with patch('tenacity.wait_exponential.__call__', return_value=0):
            gateway.execute_adapter(MockAdapter, "fail_always")


def test_gateway_retry_success():
    """Test that it recovers if a later retry succeeds."""
    global mock_call_count
    mock_call_count = 0
    gateway = AIGateway()
    
    with patch('tenacity.wait_exponential.__call__', return_value=0):
        result = gateway.execute_adapter(MockAdapter, "succeed_on_third_try")
        
    assert result == "finally success"
    assert mock_call_count == 3
