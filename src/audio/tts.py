import asyncio
import numpy as np
import sounddevice as sd
import queue
import threading
import os
import requests
import logging
import pyttsx3

logger = logging.getLogger(__name__)

class TTS:
    def __init__(self, lang_code='a', voice='af_heart', speed=1.0):
        self.lang_code = lang_code
        self.voice = voice
        self.speed = speed
        self.sample_rate = 24000
        self.audio_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._is_speaking = False
        
        # Local fallback using pyttsx3
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 175) # Speed of speech
        except Exception as e:
            print(f"TTS: Failed to initialize pyttsx3 fallback: {e}")
            self.engine = None

        # Try to initialize the local pipeline if possible
        self.pipeline = None
        try:
            from kokoro import KPipeline
            self.pipeline = KPipeline(lang_code=lang_code)
            print("TTS: Using local Kokoro pipeline.")
        except ImportError:
            print("TTS: Kokoro package not found. Will attempt to use API server at http://localhost:8880.")
        except Exception as e:
            print(f"TTS: Failed to initialize local Kokoro: {e}")

    def _play_audio_worker(self):
        """Worker thread to play audio chunks from the queue."""
        while not self._stop_event.is_set():
            try:
                audio_chunk = self.audio_queue.get(timeout=0.1)
                if audio_chunk is None: # Sentinel to stop
                    break
                sd.play(audio_chunk, self.sample_rate)
                sd.wait() # Wait for current chunk to finish
            except queue.Empty:
                continue
            except Exception as e:
                print(f"TTS Playback Error: {e}")

    async def speak(self, text_generator):
        """
        Takes a generator of text segments and streams audio.
        """
        self._stop_event.clear()
        self._is_speaking = True
        
        # If we have a local pipeline or API, we use the queue system
        # If we only have pyttsx3, we use its own system
        
        play_thread = threading.Thread(target=self._play_audio_worker)
        play_thread.start()

        try:
            full_text = ""
            async for text_segment in text_generator:
                if self._stop_event.is_set():
                    break
                full_text += text_segment
                # Synthesize on sentence boundaries or newlines
                if any(punct in text_segment for punct in ['.', '!', '?', '\n']):
                    await self._synthesize_and_queue(full_text)
                    full_text = ""
            
            if full_text.strip() and not self._stop_event.is_set():
                await self._synthesize_and_queue(full_text)
        finally:
            self.audio_queue.put(None) # Signal worker to stop
            play_thread.join()
            self._is_speaking = False

    async def _synthesize_and_queue(self, text):
        """Synthesizes text and adds the resulting audio to the playback queue."""
        text = text.strip()
        if not text:
            return

        # 1. Try local Kokoro pipeline
        if self.pipeline:
            try:
                await asyncio.to_thread(self._synthesize_local_blocking, text)
                return
            except Exception as e:
                print(f"Local synthesis error: {e}")

        # 2. Try Kokoro API server
        try:
            # remsky/kokoro-fastapi OpenAI compatible endpoint
            url = "http://localhost:8880/v1/audio/speech"
            payload = {
                "model": "kokoro",
                "input": text,
                "voice": self.voice,
                "response_format": "wav",
                "speed": self.speed
            }
            # Use to_thread to avoid blocking the event loop with requests
            response = await asyncio.to_thread(requests.post, url, json=payload, timeout=5)
            if self._stop_event.is_set():
                return
            if response.status_code == 200:
                import io
                import soundfile as sf
                data, samplerate = sf.read(io.BytesIO(response.content))
                if not self._stop_event.is_set():
                    self.audio_queue.put(data)
                    self.sample_rate = samplerate
                    return
        except Exception:
            pass # Silently fail and move to fallback

        # 3. Final Fallback: pyttsx3 (System TTS)
        if self.engine and not self._stop_event.is_set():
            try:
                # pyttsx3 is blocking, so we run it in a thread
                await asyncio.to_thread(self._pyttsx3_speak, text)
            except Exception as e:
                print(f"TTS: {text} (Audio synthesis failed: {e})")
        else:
            # If everything else fails, just print the text
            print(f"TTS: {text}")

    def _synthesize_local_blocking(self, text):
        """Blocking local synthesis that can be interrupted."""
        if self._stop_event.is_set():
            return
        generator = self.pipeline(text, voice=self.voice, speed=self.speed)
        for _, _, audio in generator:
            if self._stop_event.is_set():
                break
            self.audio_queue.put(audio)

    def _pyttsx3_speak(self, text):
        """Speak using pyttsx3."""
        if self.engine and not self._stop_event.is_set():
            self.engine.say(text)
            self.engine.runAndWait()

    def stop(self):
        """Immediately stops audio playback."""
        self._stop_event.set()
        sd.stop()
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
