# System Overview

## Runtime flow

1. **Configuration** loads from `config/settings.json` and environment overrides via `engine.config`.
2. **Engine** builds a FastAPI app (`engine.server`) and initializes the SQLite database + worker system.
3. **Control layer** classifies incoming AI tasks and guards protected paths before execution.
4. **Services** orchestrate agent memory, embeddings, vector search, and knowledge graphs. They depend only on the engine and provider interfaces.
5. **Knowledge system** wraps service primitives for long-term project insights.
6. **Bridge** exposes secure endpoints for local tooling and synchronization.
7. **Apps** compose services into end-user features (studio, builds, research, assets, deployment, sandbox).
8. **Frontend** communicates with the backend through FastAPI endpoints defined in the engine and apps.
9. **Desktop runtime** launches backend + frontend together for local development.

## Data storage

- SQLite database at `./data/agentforgeos.db` initialized by `engine.database`.
- In-memory vector store + knowledge graph for fast experimentation.
- No external AI providers are required by default.

## Background work

`engine.worker_system.WorkerSystem` schedules periodic tasks such as heartbeats or maintenance. Workers are started on app startup and shut down gracefully with the FastAPI lifecycle hooks.

## Safety

- `control.permission_matrix.yaml` lists directories that automated agents may not write to.
- `control.file_guard.FileGuard` enforces the matrix.
- `control.ai_router.AIRouter` tags risky tasks and flags protected operations.

## Extensibility

- Implement provider interfaces in `providers/` to integrate third-party AI systems.
- Add new services under `services/` while respecting dependency rules.
- Add new app modules under `apps/` without importing engine internals.
- Extend the frontend using the REST API—do not couple it directly to backend internals.
