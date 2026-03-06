import openwakeword
from openwakeword.model import Model
import numpy as np
import os

class WakeWordDetector:
    def __init__(self, wakeword_models=["hey_jarvis"], threshold=0.6):
        """
        Initializes the openWakeWord detector.
        Strictness is controlled by the threshold (0.0 to 1.0).
        """
        # openWakeWord defaults to ONNX on Windows, which is exactly what we want.
        self.oww_model = Model(
            wakeword_models=wakeword_models,
            inference_framework="onnx"
        )
        self.threshold = threshold
        # The key in predictions is usually the model name
        self.wakeword_key = wakeword_models[0]

    def predict(self, audio_chunk):
        """
        Predicts if the wake word is present in the audio chunk.
        audio_chunk should be int16, 16kHz, mono.
        """
        # Get predictions for the frame
        prediction = self.oww_model.predict(audio_chunk)
        
        # prediction is a dict: { 'wakeword_name': score }
        # The score is between 0 and 1
        score = prediction.get(self.wakeword_key, 0)
        
        if score > self.threshold:
            print(f"Wake word detected! (Score: {score:.2f})")
            return True
        return False
