# AgentForgeOS

AgentForgeOS is a clean rebuild of the AgentForge stack with a minimal, layered architecture. Each subsystem has a single responsibility and is isolated from experimental code paths.

## Layered architecture

- **engine/** – FastAPI runtime, configuration, database bootstrap, and background worker system.
- **providers/** – Abstractions for pluggable AI providers (LLM, image, TTS).
- **services/** – Core services that orchestrate agents, memory, knowledge, and vector search.
- **control/** – AI control layer for routing, supervision, and write protection.
- **knowledge/** – Knowledge system built on embeddings, vector search, and lightweight graphs.
- **bridge/** – Local machine integration and synchronization interface.
- **apps/** – Modular feature extensions (studio, builds, research, assets, deployment, sandbox).
- **frontend/** – React UI that talks to the FastAPI backend via `REACT_APP_BACKEND_URL`.
- **desktop/** – Tauri-friendly bootstrapper that starts the backend and frontend locally.
- **config/** – Runtime configuration and dependency definitions.

## Quick start

### Backend (engine)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt
python -m engine.main
```

### Frontend
```bash
cp frontend/.env.example frontend/.env
cd frontend
npm install
npm start
```

### Desktop wrapper
The desktop helper starts both backend and frontend for local development:
```bash
python desktop/bootstrap.py
```

## Documentation
- `ARCHITECTURE.md` – Layer definitions and responsibilities.
- `SYSTEM_OVERVIEW.md` – Runtime behavior and data flow.
- `DEVELOPMENT_GUIDE.md` – Local development and extension rules.
- `BOOTSTRAP_REPORT.md` – Inventory of created components and run instructions.
