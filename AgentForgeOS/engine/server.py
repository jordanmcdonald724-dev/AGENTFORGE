"""
Server entrypoint wiring FastAPI app.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

engine_dir = Path(__file__).parent
os_root = engine_dir.parent
for path in (engine_dir, os_root / "services", os_root / "providers", os_root / "apps"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

load_dotenv(os_root / "config" / ".env")

from engine.main import app  # noqa: E402

__all__ = ["app"]
