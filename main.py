import subprocess
import threading
import time

from view.app import start_frontend


def start_backend():
    subprocess.run(["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8001"])

if __name__ == "__main__":
    # Start the backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Wait for the backend to start
    time.sleep(2)

    # Start the frontend
    start_frontend()