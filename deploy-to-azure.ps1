# Azure Deployment Script for CUET UG Admission Analyzer
# Run this script in PowerShell to deploy your application to Azure

param(
    [Parameter(Mandatory=$true)]
    [string]$AppName,
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "cuet-analyzer-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$Sku = "B1"
)

Write-Host "🚀 CUET UG Admission Analyzer - Azure Deployment Script" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if Azure CLI is installed
try {
    az --version | Out-Null
    Write-Host "✅ Azure CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging into Azure..." -ForegroundColor Blue
az login

# Set subscription (if needed)
$subscriptions = az account list --query "[].{name:name, id:id}" --output table
Write-Host "📋 Available subscriptions:" -ForegroundColor Blue
Write-Host $subscriptions

# Create resource group
Write-Host "📦 Creating resource group: $ResourceGroup" -ForegroundColor Blue
az group create --name $ResourceGroup --location $Location

# Create App Service plan
$planName = "$AppName-plan"
Write-Host "🏗️  Creating App Service plan: $planName" -ForegroundColor Blue
az appservice plan create `
    --name $planName `
    --resource-group $ResourceGroup `
    --sku $Sku `
    --is-linux

# Create web app
Write-Host "🌐 Creating web app: $AppName" -ForegroundColor Blue
az webapp create `
    --name $AppName `
    --resource-group $ResourceGroup `
    --plan $planName `
    --runtime "PYTHON|3.11"

# Configure app settings
Write-Host "⚙️  Configuring app settings..." -ForegroundColor Blue
az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --settings `
        WEBSITE_PORT=8000 `
        SCM_DO_BUILD_DURING_DEPLOYMENT=true `
        ENABLE_ORYX_BUILD=true

# Set startup command
Write-Host "🚀 Setting startup command..." -ForegroundColor Blue
az webapp config set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000"

# Configure deployment source
Write-Host "📁 Configuring local git deployment..." -ForegroundColor Blue
$deploymentUrl = az webapp deployment source config-local-git `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query url `
    --output tsv

# Initialize git repository if not exists
if (-not (Test-Path ".git")) {
    Write-Host "🔧 Initializing git repository..." -ForegroundColor Blue
    git init
    git add .
    git commit -m "Initial commit for Azure deployment"
}

# Add Azure remote
Write-Host "🔗 Adding Azure remote..." -ForegroundColor Blue
git remote remove azure 2>$null  # Remove if exists
git remote add azure $deploymentUrl

# Get deployment credentials
Write-Host "🔑 Getting deployment credentials..." -ForegroundColor Blue
$credentials = az webapp deployment list-publishing-credentials `
    --name $AppName `
    --resource-group $ResourceGroup

Write-Host "📤 Deploying to Azure..." -ForegroundColor Blue
Write-Host "   This may take several minutes..." -ForegroundColor Yellow

# Deploy to Azure
try {
    git push azure main
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
} catch {
    Write-Host "❌ Deployment failed. Trying 'master' branch..." -ForegroundColor Yellow
    try {
        git push azure master
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Deployment failed. Please check your credentials and try manual deployment." -ForegroundColor Red
        Write-Host "   Deployment URL: $deploymentUrl" -ForegroundColor Yellow
    }
}

# Get app URL
$appUrl = "https://$AppName.azurewebsites.net"

Write-Host "" -ForegroundColor White
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host "🌐 Application URL: $appUrl" -ForegroundColor Blue
Write-Host "📊 Health Check: $appUrl/api/health" -ForegroundColor Blue
Write-Host "📚 API Documentation: $appUrl/docs" -ForegroundColor Blue
Write-Host "📋 Azure Portal: https://portal.azure.com" -ForegroundColor Blue
Write-Host "" -ForegroundColor White
Write-Host "🔧 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Visit your application URL to verify deployment" -ForegroundColor White
Write-Host "   2. Upload a PDF file to test functionality" -ForegroundColor White
Write-Host "   3. Monitor logs in Azure Portal if needed" -ForegroundColor White
Write-Host "" -ForegroundColor White

# Open browser to application
$openBrowser = Read-Host "Would you like to open the application in your browser? (y/n)"
if ($openBrowser.ToLower() -eq "y" -or $openBrowser.ToLower() -eq "yes") {
    Start-Process $appUrl
}

Write-Host "🚀 Happy analyzing! Your CUET UG Admission Analyzer is now live on Azure!" -ForegroundColor Green
