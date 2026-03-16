# AgentForgeOS Architecture Map

## Backend Entrypoints
- `engine/main.py` — FastAPI application with health endpoint
- `engine/server.py` — Uvicorn entrypoint exporting `app`

## Core Runtime
- `engine/config.py` — environment loader
- `engine/database.py` — MongoDB bootstrap
- `engine/worker_system.py` — async worker scheduler

## Providers
- `providers/llm_provider.py` — LLM interface (chat/stream/info)
- `providers/image_provider.py` — image generation interface
- `providers/tts_provider.py` — text-to-speech interface

## Services
- Agent orchestration: `services/agent_service.py`
- Memory: `services/memory_manager.py`
- Knowledge/graphs: `services/knowledge_graph.py`
- Vector search: `services/vector_store.py`, `services/embedding_service.py`
- Patterns: `services/pattern_extractor.py`
- Project intelligence: `services/project_genome_service.py`, `services/autopsy_service.py`

## Control Layer
- Routing: `control/ai_router.py`
- Guard: `control/file_guard.py`
- Supervision: `control/agent_supervisor.py`
- Policy: `control/permission_matrix.yaml`

## Apps
- Feature modules: `apps/studio/`, `apps/builds/`, `apps/research/`, `apps/assets/`, `apps/deployment/`, `apps/sandbox/`

## Bridge
- Local integration: `bridge/bridge_server.py`, `bridge/bridge_security.py`

## Knowledge Layer
- Shared accessors: `knowledge/knowledge_graph.py`, `knowledge/vector_store.py`, `knowledge/embedding_service.py`, `knowledge/pattern_extractor.py`

## Frontend / Desktop
- `frontend/` — placeholder for React/Vite UI
- `desktop/` — placeholder for Tauri wrapper

## Config
- `config/.env` — environment variables (placeholder)
