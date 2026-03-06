import asyncio
import numpy as np
import os
import sys

# Redirect stderr to avoid [WinError 6] in some environments
sys.stderr = open(os.devnull, 'w')

# Fix for SSL_CERT_FILE issue if it's set incorrectly in the environment
if "SSL_CERT_FILE" in os.environ and not os.path.exists(os.environ["SSL_CERT_FILE"]):
    del os.environ["SSL_CERT_FILE"]

# Disable TQDM progress bars to avoid [WinError 6] The handle is invalid
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TQDM_DISABLE"] = "1"

from src.audio.recorder import AsyncAudioRecorder
from src.audio.stt import STT
from src.audio.tts import TTS
from src.audio.wakeword import WakeWordDetector
from src.brain.llm import Brain
from src.memory.rag import LongTermMemory
import signal

class OptimusAssistant:
    def __init__(self):
        # Initialize Audio Components
        self.recorder = AsyncAudioRecorder()
        self.stt = STT(model_size="base", device="cuda")
        self.tts = TTS(voice='af_heart', speed=1.0)
        
        # JARVIS specific wake word detection
        self.wakeword_detector = WakeWordDetector(wakeword_models=["hey_jarvis"], threshold=0.7)

        # Initialize Brain & Memory
        self.brain = Brain(model_name="llama3.1:8b")
        self.memory = LongTermMemory()
        
        # Load local Stark Archives if they exist
        if os.path.exists("./archives"):
            self.memory.load_from_directory("./archives")

        self.is_running = True
        self.tts_task = None

    async def startup_sequence(self):
        """Initiate JARVIS startup sequence."""
        print("\n" + "="*50)
        print("  JARVIS OS v4.2 - SYSTEM BOOT")
        print("="*50)
        
        async def startup_text():
            yield "At your service, sir. "
            yield "Systems are online. "
            yield "MSI Vector 17 hardware is fully optimized. "
            yield "Awaiting your command."

        # Speak the startup sequence
        await self.tts.speak(startup_text())

    async def run(self):
        await self.startup_sequence()
        print("\nSay 'Hey Jarvis' to wake me up.")

        while self.is_running:
            audio_chunk = await self.recorder.get_audio_chunk()
            
            # Interruption check while speaking
            if self.tts_task and not self.tts_task.done():
                if self.recorder.is_speech(audio_chunk):
                    print("\n[JARVIS]: Interruption detected. Silencing audio.")
                    self.tts.stop()
                    try:
                        await self.tts_task
                    except asyncio.CancelledError:
                        pass
                    self.tts_task = None
                    
                    while not self.recorder.audio_queue.empty():
                        self.recorder.audio_queue.get()
                continue
            elif self.tts_task and self.tts_task.done():
                self.tts_task = None

            # Wake word detection
            if self.wakeword_detector.predict(audio_chunk):
                user_audio = await self.recorder.listen_for_speech()
                if user_audio is not None:
                    user_text = self.stt.transcribe(user_audio)
                    print(f"User: {user_text}")

                    if any(word in user_text.lower() for word in ["stand down", "exit", "quit", "stop"]):
                        async def shutdown_text():
                            yield "Understood, sir. Powering down systems. Have a pleasant evening."
                        await self.tts.speak(shutdown_text())
                        self.is_running = False
                        break

                    # Generate & Stream Response (JARVIS mode)
                    print("[JARVIS]: Processing...")
                    response_gen = self.brain.stream_response(user_text, memory=self.memory)
                    self.tts_task = asyncio.create_task(self.tts.speak(response_gen))

            await asyncio.sleep(0)

    def stop(self):
        self.is_running = False
        self.recorder.close()
        self.tts.stop()

async def main():
    assistant = OptimusAssistant()
    
    def signal_handler(sig, frame):
        print("\n[JARVIS]: Emergency shutdown initiated...")
        assistant.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    try:
        await assistant.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        assistant.stop()

if __name__ == "__main__":
    import traceback
    try:
        asyncio.run(main())
    except Exception:
        with open("crash.log", "w") as f:
            f.write(traceback.format_exc())
        print("Crashed. See crash.log")
        traceback.print_exc()
