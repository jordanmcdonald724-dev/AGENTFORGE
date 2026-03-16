# Bootstrap Report

## Components Created
- Layer directories: engine, providers, services, control, apps, bridge, knowledge, desktop, frontend, config
- Engine runtime: `engine/main.py`, `engine/server.py`, `engine/config.py`, `engine/database.py`, `engine/worker_system.py`
- Provider interfaces: `providers/llm_provider.py`, `providers/image_provider.py`, `providers/tts_provider.py`
- Services: agent orchestration, memory manager, knowledge graph, vector store, embeddings, pattern extractor, project genome, autopsy
- Control layer: AI router, file guard, agent supervisor, permission matrix
- Knowledge layer wrappers mirroring services
- Bridge layer: bridge server and security stubs
- Apps layer: starter module packages
- Documentation: ARCHITECTURE.md, SYSTEM_OVERVIEW.md, DEVELOPMENT_GUIDE.md

## How to Run
1) Backend: `cd AgentForgeOS && python -m uvicorn engine.server:app --reload --port 8001`
2) Frontend: initialize Vite/React inside `AgentForgeOS/frontend` then `npm run dev`.
3) Desktop: integrate Tauri in `desktop/` once backend/frontend run locally.

## Notes
- The engine avoids direct dependencies on external providers; inject implementations via the provider interfaces.
- Protected directories: `engine/`, `services/`, `providers/`, `control/` (see `control/permission_matrix.yaml`).
