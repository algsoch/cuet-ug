@echo off
echo ========================================
echo CUET UG Admission Analyzer - Azure Deploy
echo ========================================
echo.

REM Check if Azure CLI is installed
az --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Azure CLI is not installed.
    echo Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    pause
    exit /b 1
)

echo ✅ Azure CLI is installed

REM Get app name from user
set /p APP_NAME="Enter your app name (must be globally unique): "
if "%APP_NAME%"=="" (
    echo ❌ App name cannot be empty
    pause
    exit /b 1
)

set RESOURCE_GROUP=cuet-analyzer-rg
set LOCATION=eastus
set PLAN_NAME=%APP_NAME%-plan

echo.
echo 🔐 Logging into Azure...
az login

echo.
echo 📦 Creating resource group: %RESOURCE_GROUP%
az group create --name %RESOURCE_GROUP% --location %LOCATION%

echo.
echo 🏗️ Creating App Service plan: %PLAN_NAME%
az appservice plan create --name %PLAN_NAME% --resource-group %RESOURCE_GROUP% --sku B1 --is-linux

echo.
echo 🌐 Creating web app: %APP_NAME%
az webapp create --name %APP_NAME% --resource-group %RESOURCE_GROUP% --plan %PLAN_NAME% --runtime "PYTHON|3.11"

echo.
echo ⚙️ Configuring app settings...
az webapp config appsettings set --name %APP_NAME% --resource-group %RESOURCE_GROUP% --settings WEBSITE_PORT=8000 SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true

echo.
echo 🚀 Setting startup command...
az webapp config set --name %APP_NAME% --resource-group %RESOURCE_GROUP% --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000"

echo.
echo 📁 Configuring local git deployment...
for /f "tokens=*" %%i in ('az webapp deployment source config-local-git --name %APP_NAME% --resource-group %RESOURCE_GROUP% --query url --output tsv') do set DEPLOYMENT_URL=%%i

echo.
echo 🔧 Setting up git repository...
if not exist ".git" (
    git init
    git add .
    git commit -m "Initial commit for Azure deployment"
)

echo.
echo 🔗 Adding Azure remote...
git remote remove azure 2>nul
git remote add azure %DEPLOYMENT_URL%

echo.
echo 📤 Deploying to Azure (this may take several minutes)...
git push azure main
if %errorlevel% neq 0 (
    echo Trying master branch...
    git push azure master
)

set APP_URL=https://%APP_NAME%.azurewebsites.net

echo.
echo ========================================
echo 🎉 Deployment Complete!
echo ========================================
echo 🌐 Application URL: %APP_URL%
echo 📊 Health Check: %APP_URL%/api/health
echo 📚 API Documentation: %APP_URL%/docs
echo.
echo 🔧 Next Steps:
echo    1. Visit your application URL to verify deployment
echo    2. Upload a PDF file to test functionality
echo    3. Monitor logs in Azure Portal if needed
echo.

set /p OPEN_BROWSER="Would you like to open the application in your browser? (y/n): "
if /i "%OPEN_BROWSER%"=="y" start %APP_URL%

echo.
echo 🚀 Happy analyzing! Your CUET UG Admission Analyzer is now live on Azure!
pause
