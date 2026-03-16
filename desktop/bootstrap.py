from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    engine_cmd = [sys.executable, "-m", "engine.main"]
    frontend_cmd = ["npm", "run", "start", "--prefix", str(root / "frontend")]

    print("Starting AgentForgeOS engine...")
    engine_proc = subprocess.Popen(engine_cmd)

    print("Starting AgentForgeOS frontend (development server)...")
    frontend_proc = subprocess.Popen(frontend_cmd)

    engine_proc.wait()
    frontend_proc.wait()


if __name__ == "__main__":
    main()

