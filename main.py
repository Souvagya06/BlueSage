"""Start the BlueSage API and frontend together for local development."""

import importlib.util
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
VITE_CLI = FRONTEND_DIR / "node_modules" / "vite" / "bin" / "vite.js"


def stop_processes(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        if process.poll() is None:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def run() -> int:
    venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    python_bin = str(venv_python) if venv_python.is_file() else sys.executable

    # Test if uvicorn can be imported with selected python
    test_uvicorn = subprocess.run(
        [python_bin, "-c", "import uvicorn"],
        capture_output=True,
    )
    if test_uvicorn.returncode != 0:
        print(
            "Backend dependencies are missing. Activate the backend virtual "
            "environment and install backend\\requirements.txt first.",
            file=sys.stderr,
        )
        return 1

    node = shutil.which("node")
    if node is None:
        print("Node.js is required to run the frontend.", file=sys.stderr)
        return 1
    if not VITE_CLI.is_file():
        print(
            "Frontend dependencies are missing. Run `npm install` in the "
            "frontend folder first.",
            file=sys.stderr,
        )
        return 1

    processes = []
    try:
        processes.append(
            subprocess.Popen(
                [
                    python_bin,
                    "-m",
                    "uvicorn",
                    "main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                cwd=BACKEND_DIR,
            )
        )
        processes.append(
            subprocess.Popen(
                [node, str(VITE_CLI), "--port", "3000", "--strictPort"],
                cwd=FRONTEND_DIR,
            )
        )
        print("BlueSage is starting:")
        print("  Frontend: http://localhost:3000")
        print("  API docs: http://localhost:8000/docs")
        print("Press Ctrl+C to stop both services.")

        while True:
            for name, process in zip(("Backend", "Frontend"), processes):
                exit_code = process.poll()
                if exit_code is not None:
                    print(
                        f"{name} exited with code {exit_code}; stopping the "
                        "other service.",
                        file=sys.stderr,
                    )
                    return exit_code or 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping BlueSage...")
        return 0
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(run())
