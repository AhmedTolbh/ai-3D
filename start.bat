@echo off
REM Virtual Receptionist Avatar - Quick Start Script (Windows)
REM ============================================================

echo.
echo 🤖 Virtual Receptionist Avatar - Quick Start
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo ✓ Python found
python --version

REM Check if .env file exists
if not exist .env (
    echo.
    echo ⚠️  .env file not found
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo 📝 Please edit .env and add your API keys:
    echo    - GEMINI_API_KEY
    echo    - GOOGLE_APPLICATION_CREDENTIALS
    echo    - DID_API_KEY
    echo.
    pause
)

REM Check if virtual environment exists
if not exist venv (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo.
echo 📁 Creating directories...
if not exist static\audio mkdir static\audio
if not exist static\video mkdir static\video

REM Start the server
echo.
echo 🚀 Starting the server...
echo.
echo The application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py
