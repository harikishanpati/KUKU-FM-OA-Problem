"""
RUN APP LAUNCHER
================
Starts the Streamlit UI cleanly, preventing any Windows permission errors,
PowerShell execution policy restrictions, or email activation prompts.

Usage:
    python ui/run_app.py   (or run_app.bat from root)
"""

import os
import sys
import time
import threading
import webbrowser

project_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Direct Streamlit to local project directory to avoid permission issues
os.environ["USERPROFILE"] = project_dir
os.environ["HOME"] = project_dir
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# 2. Bypass Streamlit activation prompts
from streamlit.runtime.credentials import Credentials, _Activation
Credentials.get_current().activation = _Activation("", True)

from streamlit.web import bootstrap

if __name__ == "__main__":
    app_path = os.path.join(project_dir, "app.py")
    port = 8501
    flag_options = {
        "server.port": port,
        "server.headless": False,
        "browser.gatherUsageStats": False
    }

    print("=" * 65)
    print(f"🎬 Starting Kuku Microdrama Studio on http://localhost:{port} ...")
    print("=" * 65)

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()
    bootstrap.run(app_path, is_hello=False, args=[], flag_options=flag_options)
