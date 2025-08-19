import os
from datetime import datetime

def ts() -> str:
    return datetime.utcnow().strftime("%Y%m%d-%H%M%S")

def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path
