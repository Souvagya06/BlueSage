@echo off
cd /d "%~dp0"
echo.
echo ============================================================
echo   BlueSage -- Water Body Monitoring Platform
echo ============================================================
echo.

:: Use venv Python if available, otherwise fall back to system Python
if exist "venv\Scripts\python.exe" (
    echo Using venv Python...
    venv\Scripts\python.exe main.py %*
) else (
    echo Using system Python...
    python main.py %*
)
pause
