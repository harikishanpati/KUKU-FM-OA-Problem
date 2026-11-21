"""
RUN APP LAUNCHER — PROBLEM 2
"""
import os
import sys
import time
import threading
import webbrowser

script_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["USERPROFILE"] = script_dir
os.environ["HOME"] = script_dir
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

from streamlit.runtime.credentials import Credentials, _Activation
Credentials.get_current().activation = _Activation("", True)

from streamlit.web import bootstrap

if __name__ == "__main__":
    app_path = os.path.join(script_dir, "app.py")
    port = 8502
    flag_options = {
        "server.port": port,
        "server.headless": False,
        "browser.gatherUsageStats": False
    }

    print(f"⚖️ Starting NyayaAI at http://localhost:{port} ...")

    def open_browser():
        time.sleep(1.2)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()
    bootstrap.run(app_path, is_hello=False, args=[], flag_options=flag_options)
