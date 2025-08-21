# app/utils.py
from datetime import datetime
from pathlib import Path

def log(message: str) -> None:
    """Simple timestamped logger."""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}")

def ensure_dir(path: str | Path) -> None:
    """Create a directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)

def ts() -> str:
    """Timestamp string for filenames."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")
