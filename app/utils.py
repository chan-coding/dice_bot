from datetime import datetime

def log(message: str):
    """Simple timestamped logger for CLI output."""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}")
