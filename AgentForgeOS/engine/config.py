"""
Engine configuration loader.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).parent.parent
ENV_PATH = BASE_DIR / "config" / ".env"
load_dotenv(ENV_PATH)


def get_setting(key: str, default=None):
    return os.environ.get(key, default)
