"""
RUN APP LAUNCHER
================
Starts the Streamlit UI cleanly, preventing any Windows permission errors,
PowerShell execution policy restrictions, or email activation prompts.

Usage:
    python run_app.py
"""

import os
import sys
import time
import threading
import webbrowser

script_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# 1. Bypasses Streamlit email prompt & Windows PermissionError on ~/.streamlit
from streamlit.runtime.credentials import Credentials, _Activation
Credentials.get_current().activation = _Activation("", True)

from streamlit.web import bootstrap

if __name__ == "__main__":
    app_path = os.path.join(script_dir, "app.py")
    port = 8501
    flag_options = {
        "server.port": port,
        "server.headless": False,
        "browser.gatherUsageStats": False
    }

    print("=" * 65)
    print(f"🎬 Starting Kuku Microdrama Studio on http://localhost:{port} ...")
    print("=" * 65)

    # 2. Automatically opens your default web browser
    def open_browser():
        time.sleep(1.2)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    # 3. Starts Streamlit server
    bootstrap.run(app_path, is_hello=False, args=[], flag_options=flag_options)
