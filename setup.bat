@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher not found. Please install Python 3.11 or newer and rerun setup.
    exit /b 1
)

py -3.11 --version >nul 2>nul
if errorlevel 1 (
    echo Python 3.11 is required. Install Python 3.11 and rerun setup.
    exit /b 1
)

if not exist .venv (
    echo Creating project-local virtual environment...
    py -3.11 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "from app.database.db import initialize_database; initialize_database(); print('Database initialized successfully.')"
python health_check.py

echo.
echo Setup complete. Run run.bat to launch the application.
