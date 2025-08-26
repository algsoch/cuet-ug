@echo off
echo ========================================
echo CUET UG Admission Analyzer - Docker Deploy
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed.
    echo Please install Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

echo ✅ Docker is installed

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo You can find Docker Desktop in your Start menu or system tray.
    echo After starting Docker Desktop, wait for it to fully load, then run this script again.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Get app name from user
set /p APP_NAME="Enter your app name (default: cuet-analyzer): "
if "%APP_NAME%"=="" set APP_NAME=cuet-analyzer

echo.
echo 🏗️ Building Docker image: %APP_NAME%
echo This may take a few minutes...

REM Build Docker image
docker build -t %APP_NAME% .
if %errorlevel% neq 0 (
    echo ❌ Failed to build Docker image
    pause
    exit /b 1
)

echo ✅ Docker image built successfully

echo.
echo 🚀 Starting application container...

REM Stop any existing container
docker stop %APP_NAME% 2>nul
docker rm %APP_NAME% 2>nul

REM Run the container
docker run -d --name %APP_NAME% -p 8000:8000 -v "%cd%\data:/app/data" -v "%cd%\outputs:/app/outputs" -v "%cd%\uploads:/app/uploads" %APP_NAME%
if %errorlevel% neq 0 (
    echo ❌ Failed to start container
    pause
    exit /b 1
)

echo ✅ Container started successfully

echo.
echo ========================================
echo 🎉 Docker Deployment Complete!
echo ========================================
echo 🌐 Application URL: http://localhost:8000
echo 📊 Health Check: http://localhost:8000/api/health
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo 🔧 Docker Commands:
echo    View logs: docker logs %APP_NAME%
echo    Stop app: docker stop %APP_NAME%
echo    Start app: docker start %APP_NAME%
echo    Remove app: docker rm -f %APP_NAME%
echo.

echo ⏳ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if application is responding
curl -f http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Application is responding
) else (
    echo ⚠️ Application might still be starting. Please wait a moment and try http://localhost:8000
)

set /p OPEN_BROWSER="Would you like to open the application in your browser? (y/n): "
if /i "%OPEN_BROWSER%"=="y" start http://localhost:8000

echo.
echo 🐳 Your CUET UG Admission Analyzer is now running in Docker!
pause
