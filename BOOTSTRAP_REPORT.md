# Bootstrap Report

## Components created

- **engine/**: `main.py`, `server.py`, `config.py`, `database.py`, `worker_system.py`
- **providers/**: interface definitions for LLM, image, and TTS providers
- **services/**: agent service, memory manager, knowledge graph service, vector store, embedding service, pattern extractor, project genome, autopsy
- **control/**: AI router, file guard, agent supervisor, permission matrix
- **knowledge/**: knowledge graph, embedding, vector store, pattern extractor wrappers
- **bridge/**: bridge server router and bridge security helper
- **apps/**: starter modules for studio, builds, research, assets, deployment, sandbox
- **frontend/**: `.env.example` configured for FastAPI backend discovery
- **desktop/**: Tauri-friendly bootstrap script and notes
- **config/**: settings.json and backend requirements
- **Documentation**: README.md, ARCHITECTURE.md, SYSTEM_OVERVIEW.md, DEVELOPMENT_GUIDE.md

## How to run locally

### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt
python -m engine.main
```

Health check: `curl http://localhost:8000/health`

### Frontend
```bash
cp frontend/.env.example frontend/.env
cd frontend
npm install
npm start
```

### Desktop wrapper
```bash
python desktop/bootstrap.py
```

## Validation status

- Backend server starts via `python -m engine.main`.
- Frontend can be started via `npm start` (React).
- New modules are importable within the layered package layout.
