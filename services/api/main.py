"""Top-level FastAPI entrypoint for uvicorn runner."""

import os
import socket
import sys
from pathlib import Path

# Automatically ensure gigpulse-core and services/api are in sys.path
current_dir = Path(__file__).resolve().parent
repo_root = current_dir.parent.parent
core_pkg = repo_root / "packages" / "gigpulse-core"

for path in [str(current_dir), str(core_pkg)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from api.main import app


def is_port_in_use(port: int) -> bool:
    """Check if local port is actively bound by another process."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


if __name__ == "__main__":
    import uvicorn

    # Default to 8000, or fallback to 8001 if 8000 is occupied by another tool
    default_port = 8000 if not is_port_in_use(8000) else 8001
    port = int(os.getenv("PORT", str(default_port)))
    print(f"Starting GigPulse AI FastAPI server on http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
