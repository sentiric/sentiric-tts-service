# Sentiric TTS Service (Text-to-Speech)

**Description:** An AI service within the Sentiric platform dedicated to converting text input into natural-sounding human speech.

**Core Responsibilities:**
*   Receiving text prompts from various services.
*   Synthesizing high-quality audio waveforms in various languages and voices.
*   Returning the synthesized audio in appropriate formats (e.g., PCM, Opus, MP3).
*   Managing and updating underlying Text-to-Speech models.

**Technologies:**
*   Python
*   TensorFlow, PyTorch, or other ML frameworks
*   Flask/FastAPI (for REST API)

**API Interactions (As an API Provider):**
*   Exposes a RESTful API for `sentiric-agent-service` and `sentiric-api-gateway-service` to request text-to-speech conversions.

**Local Development:**
1.  Clone this repository: `git clone https://github.com/sentiric/sentiric-tts-service.git`
2.  Navigate into the directory: `cd sentiric-tts-service`
3.  Create a virtual environment and install dependencies: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
4.  Create a `.env` file from `.env.example` (if any).
5.  Start the service: `python app.py` (or equivalent).

**Configuration:**
Refer to `config/` directory and `.env.example` for service-specific configurations.

**Deployment:**
Designed for containerized deployment (e.g., Docker, Kubernetes), potentially with GPU acceleration if using advanced models. Refer to `sentiric-infrastructure`.

**Contributing:**
We welcome contributions! Please refer to the [Sentiric Governance](https://github.com/sentiric/sentiric-governance) repository for coding standards and contribution guidelines.

**License:**
This project is licensed under the [License](LICENSE).
