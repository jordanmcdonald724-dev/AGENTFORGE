# Development Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt
python -m engine.main
```

- Configuration lives in `config/settings.json` with environment variable overrides (`AGENTFORGE_*`).
- Database defaults to SQLite at `./data/agentforgeos.db`.

## Frontend setup

```bash
cp frontend/.env.example frontend/.env
cd frontend
npm install
npm start          # dev server
npm run build      # production build
```

Set `REACT_APP_BACKEND_URL` to the FastAPI host/port.

## Desktop runtime

Use `python desktop/bootstrap.py` to start backend + frontend together. Wire this into the Tauri Rust sidecar when creating the desktop bundle.

## Extending the system

- **Providers:** Implement `providers.llm_provider.LLMProvider`, `providers.image_provider.ImageProvider`, or `providers.tts_provider.TTSProvider` to add new integrations.
- **Services:** Build new orchestrators that rely only on engine + provider interfaces.
- **Apps:** Add new modules under `apps/` to expose features without touching engine internals.
- **Control:** Update `permission_matrix.yaml` carefully to maintain safety boundaries.

## Testing

- Unit tests are placed in `tests/`.
- Run tests with `python -m pytest`.
- Keep tests focused and align them with the layered architecture rules.
