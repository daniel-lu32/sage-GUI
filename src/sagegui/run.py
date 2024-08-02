import subprocess
import os
import signal
import sys

def main():

    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gui.py"))
    run_script = ["streamlit", "run", script_path, "--server.maxUploadSize=8000"]

    # Run the streamlit app with specified arguments
    process = subprocess.Popen(run_script)

    def signal_handler(sig, frame):
        print("Terminating Streamlit process...")
        process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    process.wait()

if __name__ == "__main__":
    main()