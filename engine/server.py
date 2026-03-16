from __future__ import annotations

from fastapi import Depends, FastAPI

from bridge.bridge_server import get_router as get_bridge_router
from .config import Settings, get_settings
from .database import Database, init_database
from .worker_system import WorkerSystem


def create_app(
    settings: Settings | None = None,
    database: Database | None = None,
    worker_system: WorkerSystem | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    db = database or init_database(settings)
    workers = worker_system or WorkerSystem()

    app = FastAPI(title=settings.app_name, version="0.1.0", docs_url="/api/docs")

    @app.on_event("startup")
    async def _startup() -> None:
        db.record_event("startup")

        async def heartbeat() -> None:
            db.record_event("heartbeat")

        workers.add_periodic_task(heartbeat, interval_seconds=60)
        await workers.start()

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await workers.shutdown()
        db.record_event("shutdown")
        db.close()

    @app.get("/health")
    def health(current_settings: Settings = Depends(get_settings)) -> dict:
        return {
            "message": "ok",
            "version": app.version,
            "environment": current_settings.environment,
            "features": ["engine", "services", "providers", "control", "bridge", "apps"],
        }

    @app.get("/config")
    def config(current_settings: Settings = Depends(get_settings)) -> dict:
        return {
            "app_name": current_settings.app_name,
            "environment": current_settings.environment,
            "host": current_settings.host,
            "port": current_settings.port,
        }

    app.include_router(get_bridge_router())

    return app
