# AgentForgeOS Desktop Runtime

The desktop runtime is a Tauri-friendly wrapper that launches the backend engine and the React frontend locally. The goal is to provide a single executable that boots the API and UI for offline development.

## Development bootstrap

```bash
python desktop/bootstrap.py
```

This helper starts:
1) the FastAPI engine on the configured port
2) the React frontend dev server

Tauri can consume this script when wiring the Rust sidecar so the correct processes are orchestrated before the webview loads.
