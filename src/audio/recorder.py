import asyncio
import numpy as np
import pyaudio
import torch
import collections
import threading
import queue

class AsyncAudioRecorder:
    def __init__(self, rate=16000, chunk=1280, vad_threshold=0.5):
        """
        chunk=1280 (80ms) is ideal for openWakeWord.
        """
        self.rate = rate
        self.chunk = chunk
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk
        )
        # Avoid ONNX Runtime GPU to prevent missing CUDA DLL issues on Windows.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.vad_model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.vad_model.to(self.device)
        except Exception as e:
            print(f"Recorder VAD: Failed to init on {self.device} ({e}). Falling back to CPU.")
            self.device = "cpu"
            self.vad_model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.vad_model.to(self.device)
        self.vad_threshold = vad_threshold
        
        # Internal queue for audio chunks
        self.audio_queue = queue.Queue(maxsize=100)
        self._stop_event = threading.Event()
        self._read_thread = threading.Thread(target=self._read_stream_worker, daemon=True)
        self._read_thread.start()

    def _read_stream_worker(self):
        """Background thread to constantly read from the PyAudio stream."""
        while not self._stop_event.is_set():
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                if not self.audio_queue.full():
                    self.audio_queue.put(np.frombuffer(data, dtype=np.int16))
            except Exception as e:
                print(f"Recorder Error: {e}")
                break

    async def get_audio_chunk(self):
        """Retrieves the next chunk from the internal queue."""
        while self.audio_queue.empty():
            await asyncio.sleep(0.01)
        return self.audio_queue.get()

    def is_speech(self, audio_chunk):
        """Checks if the chunk contains speech using VAD."""
        # Convert int16 to float32 as expected by Silero VAD
        audio_float32 = audio_chunk.astype(np.float32) / 32768.0
        # Silero VAD expects a tensor of shape [1, length]
        tensor_chunk = torch.from_numpy(audio_float32).unsqueeze(0).to(self.device)
        speech_prob = self.vad_model(tensor_chunk, self.rate).item()
        return speech_prob > self.vad_threshold

    async def listen_for_speech(self):
        """Listens until speech starts, then continues until speech ends."""
        print("Listening for command...")
        recorded_frames = []
        speech_started = False
        silent_chunks = 0
        # Wait up to 5 seconds for speech to start
        max_start_wait = int(self.rate / self.chunk * 5)
        # 1.5 seconds of silence to end
        max_silent_chunks = int(self.rate / self.chunk * 1.5)

        for _ in range(max_start_wait):
            chunk = await self.get_audio_chunk()
            if self.is_speech(chunk):
                speech_started = True
                recorded_frames.append(chunk)
                break
            await asyncio.sleep(0)
        
        if not speech_started:
            print("No speech detected.")
            return None

        print("Speech detected! Listening...")
        while True:
            chunk = await self.get_audio_chunk()
            recorded_frames.append(chunk)
            if self.is_speech(chunk):
                silent_chunks = 0
            else:
                silent_chunks += 1
                if silent_chunks > max_silent_chunks:
                    print("Speech ended.")
                    break
            await asyncio.sleep(0)

        if recorded_frames:
            return np.concatenate(recorded_frames)
        return None

    def close(self):
        self._stop_event.set()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        if self._read_thread.is_alive():
            self._read_thread.join(timeout=1)
