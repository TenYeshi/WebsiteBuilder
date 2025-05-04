import subprocess
import sys
import time

def run_app():
    print("Starting Flask application...")
    try:
        subprocess.Popen([sys.executable, "main.py"])
        print("Application started successfully!")
        print("Access the application at: http://localhost:5000")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    run_app()
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Launcher stopped")