import webview
import threading
import subprocess
import time
import os
import requests

def start_flet():
    subprocess.Popen(
        ["python", "rephrase_app.py"],
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    )
    for _ in range(10):
        try:
            requests.get("http://localhost:8550")
            return
        except:
            time.sleep(3)

if __name__ == "__main__":
    threading.Thread(target=start_flet, daemon=True).start()
    webview.create_window(
        "言い換えアプリ",
        "http://localhost:8551",
        width=600,
        height=400,
        x=100,
        y=100,
        resizable=False
    )
    webview.start()
