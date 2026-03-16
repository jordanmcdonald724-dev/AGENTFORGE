# Phase Audit – What changed (facts from diff vs `origin/main`)

Scope: comparing this branch to `origin/main` to enumerate exactly what was altered.

## Files removed or effectively broken
- `backend/main.py`, `backend/server.py`, `backend/server_modular_wrapper.py` **removed**.
- `backend/routes/` moved to `AgentForgeOS/apps/routes/` with small edits; imports/tests expecting `backend.routes.*` will fail.
- `frontend/` real project removed; replaced by a symlink to `AgentForgeOS/desktop/frontend` (placeholder UI).
- `.gitignore` replaced by cache-pack listings and repeated env entries; original ignores lost.

## Files added
- New architecture docs: `AgentForgeOS/{ARCHITECTURE.md, ARCHITECTURE_MAP.md, BOOTSTRAP_REPORT.md, DEVELOPMENT_GUIDE.md, RESTRUCTURE_REPORT.md, SYSTEM_OVERVIEW.md}`.
- New runtime skeleton under `AgentForgeOS/engine`, provider/service/control layers, and placeholder desktop/frontend packages.
- `PR_AUDIT.md` (previous audit) at repo root.

## Files moved/renamed (without backward shims)
- Root `apps/` packages moved under `AgentForgeOS/apps/` (same modules, new namespace).
- Legacy `backend/` routes moved under `AgentForgeOS/apps/routes/`; engine/server pieces recreated under `AgentForgeOS/engine/`.
- `bridge/` -> `AgentForgeOS/bridge/`
- `control/` -> `AgentForgeOS/control/`
- `engine/` and `config/` -> `AgentForgeOS/engine/` + `AgentForgeOS/config/`
- `knowledge/` -> `AgentForgeOS/knowledge/`
- `providers/` -> `AgentForgeOS/engine/`
- `services/` -> `AgentForgeOS/engine/core/` and `AgentForgeOS/services/`

## Behavior impact
- Legacy API entrypoints are gone; commands like `uvicorn backend.main:app` or tests importing `backend` modules will fail.
- Frontend build scripts targeting `frontend/` now point at an uninitialized placeholder via symlink.
- Git ignore hygiene compromised; risk of committing caches/env files.

## Next steps (to restore stability)
1. Restore or shim legacy `backend/*` modules so existing tests and scripts work.
2. Reinstate the original `frontend/` project or update tooling to target the new path.
3. Revert `.gitignore` to the clean `origin/main` version.
4. Keep the `AgentForgeOS/` skeleton isolated until wired and tested.
