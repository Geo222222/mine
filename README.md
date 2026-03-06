# Optimus - JARVIS Protocol v4.2

Optimus is an autonomous, voice-activated AI assistant designed to operate as a digital partner on high-performance machines. Originally built by Tony Stark (as JARVIS), this implementation is specifically tuned for the **MSI Vector 17** hardware environment.

## 🚀 Core Capabilities

- **🎙️ Strict Wake Word Detection**: Uses `openWakeWord` with a high-precision ONNX model to listen specifically for *"Hey Jarvis"*.
- **🧠 ReAct Autonomous Brain**: Powered by LangGraph and Ollama (Llama 3.1:8b), JARVIS can reason, call tools, and handle complex multi-step instructions.
- **🖥️ Hardware Telemetry**: Specialized monitoring for MSI Vector 17, including CPU frequencies, NVIDIA GPU clock speeds, VRAM, and thermal status.
- **🔊 Multi-Tier TTS**: Natural AI speech using the Kokoro pipeline, with an automatic offline fallback to system SAPI5 voices.
- **📁 Stark Archives (RAG)**: Long-term memory storage for personal notes and project documents using ChromaDB.
- **🛠️ System & Web Tools**: Ability to control media, volume, launch applications (Chrome, VS Code, Spotify), and perform real-time web searches via the Tavily engine.

## 🔮 Future Roadmap

For planned technical evolutions, see [FUTURE_UPGRADES.md](file:///c:/Users/epinn/Documents/dev/optimus/FUTURE_UPGRADES.md).

## 🛠️ Hardware Setup (MSI Vector 17)

To ensure full diagnostic capabilities, ensure the following are installed:
- **NVIDIA Drivers**: Required for `nvidia-smi` GPU telemetry.
- **Python 3.9+**: Recommended environment.
- **Ollama**: Local LLM server running `llama3.1:8b`.

## 📦 Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Geo222222/mine.git
    cd optimus
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment**:
    Create a `.env` file for API keys (e.g., Tavily):
    ```env
    TAVILY_API_KEY=your_key_here
    ```

## 🎮 Operation

To initiate the JARVIS startup sequence:
```bash
python optimus.py
```

- **Wake Word**: Say *"Hey Jarvis"*.
- **Status Report**: *"Jarvis, what's the status of my systems?"*
- **App Launch**: *"Launch VS Code."*
- **Media**: *"Increase the volume."*
- **Shutdown**: *"Jarvis, stand down"* or *"Power down systems"*.

## 🧪 Testing

The system includes a suite of automated and manual tests in the `tests/` directory:
- **System Vitals**: `pytest tests/test_system.py`
- **Voice Synthesis**: `python tests/test_voice.py`
- **Autonomous Reasoning**: `python tests/test_brain.py`

---
*"At your service, sir."*
