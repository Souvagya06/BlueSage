@echo off
cd /d "%~dp0"
echo Starting BlueSage Full Application...
if exist "backend\venv\Scripts\python.exe" (
    backend\venv\Scripts\python.exe main.py
) else (
    python main.py
)
pause

