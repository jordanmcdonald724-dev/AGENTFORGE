# AgentForgeOS Architecture

AgentForgeOS is intentionally minimal and layered. Each layer has a dedicated responsibility and should only depend on the layer(s) beneath it.

## Layers

| Layer | Responsibility | Allowed Dependencies |
| --- | --- | --- |
| engine | Runtime bootstrap, FastAPI server, configuration, database, worker system | Standard library, FastAPI |
| providers | Abstractions for external AI systems (LLM, image, TTS) | engine |
| services | Internal business services (agents, memory, embeddings, knowledge graph, vector search, pattern analysis) | engine, providers |
| control | Safety gates: AI routing, file guard, supervision, permission matrix | engine |
| knowledge | Knowledge system reusing embeddings, vector search, and pattern extraction | engine, services |
| bridge | Local integration endpoints and security guardrails | engine |
| apps | Feature modules that compose services/providers without touching engine internals | engine, services, providers |
| frontend | React client that communicates with the FastAPI API surface | API only |
| desktop | Tauri-friendly launcher that starts backend + frontend | engine, frontend |

## Rules

1. Do **not** bypass the control layer when modifying code.
2. Keep provider implementations pluggable; only the interfaces live in `providers/`.
3. Services must remain AI-provider-agnostic and rely solely on defined interfaces.
4. Knowledge layer should consume services instead of re-implementing them.
5. Apps must not import engine internals directly—use services/providers.
6. Protected directories listed in `control/permission_matrix.yaml` are write-restricted for automated agents.
