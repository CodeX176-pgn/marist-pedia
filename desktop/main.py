"""
Marist Pedia desktop launcher.

This file is responsible for starting the desktop application window.
The actual quiz logic remains inside the FastAPI backend.
"""

import threading
import time
from pathlib import Path

import uvicorn
import webview
from app.config.settings import settings

# Find the main project directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# The frontend entry page that the desktop window will display.
FRONTEND_INDEX = PROJECT_ROOT / "frontend" / "index.html"


def start_backend() -> None:
    """
    Start FastAPI in the background.

    The backend runs in another thread so that the desktop window
    remains responsive while FastAPI is running.
    """

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        workers=1,
    )


def wait_for_backend() -> None:
    """
    Give FastAPI a moment to start before opening the UI.

    This is a simple first version. Later we can replace this
    with an actual health-check loop.
    """

    time.sleep(1)


def main() -> None:
    """Start the Marist Pedia desktop application."""

    if not FRONTEND_INDEX.exists():
        raise FileNotFoundError(
            f"Frontend entry page was not found: {FRONTEND_INDEX}"
        )

    # Start FastAPI without blocking the desktop window.
    backend_thread = threading.Thread(
        target=start_backend,
        daemon=True,
    )
    backend_thread.start()

    # Give the backend a short moment to start.
    wait_for_backend()

    # Open the HTML application inside a desktop window.
    webview.create_window(
        "Marist Pedia",
        str(FRONTEND_INDEX),
        width=1200,
        height=800,
        min_size=(900, 600),
        resizable=True,
    )

    # Start the native desktop window.
    webview.start()


if __name__ == "__main__":
    main()