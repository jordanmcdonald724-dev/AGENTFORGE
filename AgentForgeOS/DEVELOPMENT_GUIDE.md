# Development Guide

## Prerequisites
- Python 3.11+
- Node 18+ (for frontend)
- MongoDB (local or remote)

## Backend (Engine)
```bash
cd AgentForgeOS
python -m uvicorn engine.server:app --reload --port 8001
```

## Frontend
The frontend directory is present for future React/Vite code. Initialize with your preferred tooling:
```bash
cd AgentForgeOS/frontend
npm create vite@latest .
npm install
npm run dev
```

## Desktop
The `desktop/` folder is reserved for a Tauri wrapper. Run the backend and frontend locally, then integrate Tauri when ready.

## Adding Providers
Implement `LLMProvider`, `ImageProvider`, or `TTSProvider` in `providers/` and inject into services.

## Safety
Protected layers: `engine/`, `services/`, `providers/`, `control/`. Use `control/file_guard.py` for write checks.
