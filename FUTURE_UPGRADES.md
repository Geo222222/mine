# JARVIS Protocol: Future Upgrades & Stark Initiatives

This document outlines the planned technical evolutions for the JARVIS/Optimus assistant, specifically tailored for the high-performance MSI Vector 17 environment.

---

## 🏗️ Phase 1: The "Iron Vitals" Subroutine
**Objective**: Transition from reactive telemetry to proactive system management.

- [ ] **Proactive Thermal Alerts**: Implement a background monitoring thread that alerts the user if CPU/GPU temperatures exceed 85°C.
- [ ] **Power Optimization**: Detect when the machine switches to battery and automatically suggest low-latency/low-power LLM modes.
- [ ] **MSI Center Integration**: Attempt to hook into MSI-specific SDKs for fan control and performance profile switching.

## 🌐 Phase 2: Project "House Party" (Autonomous Tooling)
**Objective**: Give JARVIS the ability to *interact* with the digital world, not just launch it.

- [ ] **Browser Tool Use**: Integrate Playwright or Selenium tools so JARVIS can navigate websites, fill forms, and extract real-time data from complex JS-heavy sites.
- [ ] **File System Mastery**: Allow JARVIS to perform file operations (move, rename, zip) with safety guardrails.
- [ ] **Multi-App Orchestration**: Automate sequences like "Jarvis, prepare for coding" which launches VS Code, Spotify, and a local dev server simultaneously.

## 🧠 Phase 3: Stark Industries "Omnisearch" (Cross-Project RAG)
**Objective**: Unified intelligence across all local development projects.

- [ ] **Multi-Directory Ingestion**: Expand the Stark Archives to monitor multiple root paths (e.g., `optimus/`, `chair-sense/`).
- [ ] **Code-Specific Embedding**: Use a code-aware embedding model (like `unixcoder` or `codebert`) for better retrieval of technical implementation details.
- [ ] **Contextual Linking**: Allow JARVIS to reference solutions from past projects when solving current tasks.

## 👁️ Phase 4: "DUM-E" Mode (Vision & Presence)
**Objective**: Give JARVIS visual context and spatial awareness.

- [ ] **Webcam Presence Detection**: Use a lightweight vision model to detect when the user is at the desk and offer a "Welcome back" sequence.
- [ ] **Screen Contextualization**: Implement screen-capture tools so the user can say "Jarvis, look at this error" and have him analyze the active window.

## 🎙️ Phase 5: The "Optimus" Protocol (Custom Identity)
**Objective**: Fully personalized identity and voice.

- [ ] **Custom Wake Word Training**: Record 100+ samples of "Optimus" and train a specialized `.onnx` model using the `openWakeWord` training pipeline.
- [ ] **Voice Cloning (V2)**: Implement zero-shot voice cloning using the local GPU (RTX 40-series) for even more natural, custom-voiced responses.

---
*"The suit and I are one."* — JARVIS Protocol v5.0 Roadmap
