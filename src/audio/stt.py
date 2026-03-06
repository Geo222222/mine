from faster_whisper import WhisperModel
import numpy as np

def _init_whisper_model(model_size, device, compute_type):
    """Initialize Whisper model with safe GPU fallback on Windows."""
    try:
        return WhisperModel(model_size, device=device, compute_type=compute_type)
    except Exception as e:
        # Common failure: missing CUDA runtime DLLs like cublas64_12.dll
        print(f"STT: Failed to init on {device} ({e}). Falling back to CPU.")
        return WhisperModel(model_size, device="cpu", compute_type="int8")

class STT:
    def __init__(self, model_size="base", device="cuda", compute_type="float16"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = _init_whisper_model(model_size, device, compute_type)

    def transcribe(self, audio_data):
        """Transcribes audio data (numpy array) to text."""
        # Whisper expects float32 in range [-1, 1]
        audio_float32 = audio_data.astype(np.float32) / 32768.0
        try:
            segments, info = self.model.transcribe(audio_float32, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            # Retry on CPU if CUDA runtime DLLs are missing or GPU fails mid-run
            print(f"STT: Transcribe failed ({e}). Retrying on CPU.")
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            segments, info = self.model.transcribe(audio_float32, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
