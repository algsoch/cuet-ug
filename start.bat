@echo off
REM DU Admission Analyzer - Windows Startup Script
REM Full Stack Web Application

echo.
echo ===================================
echo  DU Admission Analyzer
echo  Full Stack Web Application
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% detected

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip >nul 2>&1

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Some dependencies may have failed to install
    echo The application may still work with basic functionality
)

REM Create necessary directories
if not exist "data" mkdir data
if not exist "outputs" mkdir outputs
if not exist "uploads" mkdir uploads
if not exist "static" mkdir static
if not exist "templates" mkdir templates

REM Check for Java (optional for PDF processing)
java -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Warning: Java not found
    echo Some PDF extraction features may not work optimally
    echo Consider installing Java 8 or higher for best performance
    echo.
)

REM Start the application
echo.
echo Starting DU Admission Analyzer...
echo.
echo The application will open in your default browser
echo Press Ctrl+C to stop the server
echo.

REM Find available port
set PORT=8000
netstat -an | find ":%PORT% " >nul
if not errorlevel 1 (
    set PORT=8001
    netstat -an | find ":%PORT% " >nul
    if not errorlevel 1 (
        set PORT=8002
    )
)

echo Starting server on port %PORT%...
echo Application URL: http://localhost:%PORT%
echo.

REM Start the FastAPI server
python -m uvicorn app:app --host 0.0.0.0 --port %PORT% --reload

REM Cleanup on exit
echo.
echo Server stopped.
deactivate
pause
