import pytest
from src.tools.system_tools import SystemTools

def test_system_telemetry():
    """Verify that system telemetry returns expected keys."""
    tools = SystemTools()
    telemetry = tools.get_system_telemetry()
    
    expected_keys = ["device", "cpu_usage", "memory_usage", "os", "disk_usage"]
    for key in expected_keys:
        assert key in telemetry
        assert isinstance(telemetry[key], str)
    
    print("System telemetry test passed.")

def test_media_control_invalid():
    """Verify that invalid media control actions return an error message."""
    tools = SystemTools()
    result = tools.control_media("invalid_action")
    assert "error" in result.lower() or "not recognized" in result.lower()
    print("Media control invalid action test passed.")
