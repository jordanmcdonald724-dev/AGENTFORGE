# AgentForgeOS Architecture

AgentForgeOS is organized into clean, minimal layers:

- **engine/** — runtime, FastAPI app, config, database, workers
- **providers/** — external AI provider interfaces
- **services/** — internal orchestration and intelligence services
- **control/** — safety layer enforcing permissions and supervision
- **apps/** — feature modules (studio, builds, research, assets, deployment, sandbox)
- **bridge/** — local integration utilities
- **knowledge/** — shared knowledge/embedding utilities
- **desktop/** — desktop runtime wrapper
- **frontend/** — web UI
- **config/** — environment and settings
