# System Overview

AgentForgeOS provides a layered platform for AI-assisted development:

- The **engine** hosts the FastAPI server and bootstraps configuration, database, and worker systems.
- **providers** define interfaces for LLM, image, and TTS services so implementations can be swapped.
- **services** implement orchestration, memory, embeddings, vector search, pattern extraction, and project intelligence.
- **control** protects core layers with routing, guards, and supervision.
- **apps** deliver user-facing features (studio, builds, research, assets, deployment, sandbox).
- **bridge** handles local-machine integrations.
- **knowledge** exposes shared knowledge utilities for read-heavy flows.
- **frontend** and **desktop** deliver UI surfaces.
