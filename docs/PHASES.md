# Phases Overview (current PR branch vs `origin/main`)

This file records the intended phases and the current state observed in this branch.

## What was expected
- Keep legacy runtime working (`backend/main.py`, `backend/server.py`, `backend/routes/*`, tests).
- Avoid wholesale rewrites; introduce new architecture behind feature flags/parallel paths.
- Preserve existing frontend path (`frontend/` real project tree, not a symlink).
- Keep repository hygiene intact (clean `.gitignore`, no stray cache blobs).

## What actually landed in this branch
1) **Backend relocation/removal**
   - Legacy FastAPI entrypoints and routes were moved into `AgentForgeOS/engine` and `AgentForgeOS/apps` without compatibility shims.
   - `backend/main.py`, `backend/server.py`, and `backend/server_modular_wrapper.py` are missing; `backend/` now only holds `core/` and `tests/`, so imports/tests targeting `backend.*` break.

2) **Frontend replacement**
   - `frontend/` was replaced by a symlink pointing to `AgentForgeOS/desktop/frontend`, a placeholder UI. Tooling expecting the original `frontend` project will fail.

3) **Repository ignore rules corrupted**
   - `.gitignore` was overwritten with repeated `frontend/node_modules/.cache/...` pack entries and stray `-e` lines; standard ignores (env files, build outputs, caches) from `origin/main` were lost.

4) **Large-scale path moves**
   - `apps/`, `backend/`, `bridge/`, `control/`, `engine/`, `knowledge/`, `providers/`, `services/` were relocated under a new `AgentForgeOS/` namespace.
   - New docs added under `AgentForgeOS/` describing the new layout, but no bridging adapters for legacy code.

5) **Risk**
   - Existing tests and deployment scripts referencing legacy paths will fail until shims or reversions are added.

