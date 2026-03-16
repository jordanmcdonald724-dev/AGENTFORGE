from __future__ import annotations

import uvicorn

from .config import get_settings
from .server import create_app


def run() -> None:
    settings = get_settings()
    app = create_app(settings=settings)
    uvicorn.run(app, host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    run()

