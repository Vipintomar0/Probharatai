@echo off
REM ProBharatAI One-Command Installer for Windows
echo.
echo  ==========================================
echo   ProBharatAI - AI Desktop Automation
echo  ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found

REM Create virtual environment
echo.
echo [INFO] Setting up Python environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install backend dependencies
echo [INFO] Installing backend dependencies...
pip install -r backend\requirements.txt

REM Install Playwright
echo [INFO] Installing browser automation...
python -m playwright install chromium

REM Install frontend
echo [INFO] Installing frontend...
cd frontend
call npm install
cd ..

REM Setup env
if not exist backend\.env (
    copy backend\.env.example backend\.env
    echo [OK] Created .env configuration file
)

echo.
echo  ==========================================
echo   ProBharatAI installed successfully!
echo  ==========================================
echo.
echo  Quick Start:
echo    python cli.py start     - Start the platform
echo    python cli.py status    - Check status
echo    python cli.py run "Search AI jobs"
echo.
echo  Dashboard: http://localhost:3000
echo  API:       http://localhost:8000
echo.
pause
