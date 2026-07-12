# AI Provider Setup & Configuration

This guide provides instructions for configuring, running, and troubleshooting the SpeakLift AI Infrastructure.

## 1. Architecture Overview
SpeakLift utilizes a highly decoupled, provider-agnostic AI subsystem. The Business Layer communicates strictly with the `LLMService`, which orchestrates prompts through an `LLMRouter`. The router gracefully fails over between local and cloud providers (`OllamaProvider`, `GeminiProvider`) according to the active `LLM_ROUTING_STRATEGY`.

## 2. Supported Providers
- **Gemini**: Google's cloud-based LLM, powered by the `google-genai` Python SDK.
- **Ollama**: Local inference engine for running open-weights models.

## 3. Environment Configuration
The AI subsystem is controlled via variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_DEFAULT_PROVIDER` | `ollama` | Defines the primary provider to utilize first within a tier. |
| `LLM_ROUTING_STRATEGY` | `prefer_local` | Defines fallback order: `prefer_local`, `prefer_cloud`, `local_only`, `cloud_only`. |
| `LLM_TEMPERATURE` | `0.7` | Global fallback temperature for completion requests. |
| `LLM_MAX_OUTPUT_TOKENS` | `2048` | Global fallback maximum output length. |
| `GEMINI_API_KEY` | (None) | Required for the Gemini provider. Must be obtained from Google AI Studio. |
| `GEMINI_DEFAULT_MODEL` | `gemini-3.5-flash` | The specific Google model to use. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | The URL of the local Ollama daemon. |
| `OLLAMA_DEFAULT_MODEL` | `qwen3:8b` | The local model to use. See recommendation below. |

## 4. Gemini Setup
1. **API Key**: Generate a key from [Google AI Studio](https://aistudio.google.com/).
2. **Configuration**: Add `GEMINI_API_KEY=your_key_here` to `backend/.env`.
3. **Testing**: Gemini requires internet egress. Integration tests will automatically skip if the key is absent.

## 5. Ollama Setup
1. **Installation**: Download from [Ollama.com](https://ollama.com/download) or install via brew: `brew install ollama`.
2. **Running**: Start the daemon (`ollama serve` or via the system tray app).
3. **Pulling Models**: Run `ollama run <model_name>` to download and test a model.

## 6. Recommended Local Model
We officially recommend **Qwen 3 8B Instruct** (`qwen3:8b`). 
*Why?* Qwen 3 offers state-of-the-art reasoning, excellent JSON adherence, and remarkably fast local inference speeds, making it ideal for the deterministic evaluation pipeline without requiring massive VRAM footprint.
Run `ollama pull qwen3:8b` to install it, and update `OLLAMA_DEFAULT_MODEL=qwen3:8b` in your `.env`.

## 7. Running Tests
The AI subsystem is heavily tested without requiring live API keys.
- **Unit Tests**: Mocks the SDK boundaries. Run `pytest backend/tests/ai/`.
- **Integration Tests**: Hit the live providers. Automatically skipped if unavailable. Run `pytest backend/tests/ai/ -m integration`.
- **Smoke Test**: To manually verify the live pipeline, run: `python backend/scripts/smoke_test_ai.py`.

## 8. Troubleshooting
- **Missing API Key**: Ensure `GEMINI_API_KEY` is precisely set in `backend/.env`. The provider will throw an `AIConfigurationError` otherwise when selected.
- **Ollama Unavailable**: If you encounter connection errors, verify Ollama is running (`curl http://localhost:11434/api/tags`).
- **Model Not Downloaded**: If Ollama throws a 404 Model Not Found, you must manually pull the model via `ollama pull <model_name>`.
- **Mixed Output (Streaming)**: The `LLMRouter` guarantees stream consistency; if a stream crashes midway, it intentionally halts instead of injecting fallback output.
