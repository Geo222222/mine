import pytest
from src.audio.tts import TTS

def test_tts_initialization():
    """Verify that the TTS component can be initialized."""
    tts = TTS()
    assert tts is not None
    # Check if the fallback engine is initialized
    assert tts.engine is not None or tts.pipeline is not None
    print("TTS initialization test passed.")

def test_tts_stop():
    """Verify that the TTS component's stop method works."""
    tts = TTS()
    tts.stop()
    assert tts._stop_event.is_set()
    print("TTS stop test passed.")
