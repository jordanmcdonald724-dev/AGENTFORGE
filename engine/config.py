from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional


CONFIG_ROOT = Path(__file__).resolve().parent.parent / "config"
DEFAULT_SETTINGS_PATH = CONFIG_ROOT / "settings.json"


@dataclass
class Settings:
    """Lightweight configuration loader for the AgentForgeOS runtime."""

    app_name: str = "AgentForgeOS"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "sqlite:///./data/agentforgeos.db"
    worker_concurrency: int = 2

    @classmethod
    def from_mapping(cls, data: Dict[str, Any]) -> "Settings":
        return cls(
            app_name=data.get("app_name", cls.app_name),
            environment=data.get("environment", cls.environment),
            host=data.get("host", cls.host),
            port=int(data.get("port", cls.port)),
            database_url=data.get("database_url", cls.database_url),
            worker_concurrency=int(data.get("worker_concurrency", cls.worker_concurrency)),
        )


def _load_file_settings(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        return {}
    if config_path.suffix.lower() == ".json":
        return json.loads(config_path.read_text())
    raise ValueError(f"Unsupported config format: {config_path.suffix}")


def load_settings(config_path: Optional[Path] = None) -> Settings:
    """Load settings from disk and environment variables."""
    path = config_path or DEFAULT_SETTINGS_PATH
    file_settings = _load_file_settings(path) if path else {}

    env_overrides: Dict[str, Any] = {
        "app_name": os.getenv("AGENTFORGE_APP_NAME"),
        "environment": os.getenv("AGENTFORGE_ENV", os.getenv("ENVIRONMENT")),
        "host": os.getenv("AGENTFORGE_HOST"),
        "port": os.getenv("AGENTFORGE_PORT"),
        "database_url": os.getenv("AGENTFORGE_DATABASE_URL"),
        "worker_concurrency": os.getenv("AGENTFORGE_WORKERS"),
    }

    merged: Dict[str, Any] = {**file_settings, **{k: v for k, v in env_overrides.items() if v is not None}}
    return Settings.from_mapping(merged)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings access for FastAPI dependency injection."""
    return load_settings()


def reload_settings() -> Settings:
    """Refresh cached settings after config changes."""
    get_settings.cache_clear()
    return get_settings()

