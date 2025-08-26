# CUET UG Admission Analyzer - Azure Deployment Guide

## 🚀 Complete Azure App Service Deployment

This guide will help you deploy your CUET UG Admission Analyzer application to Azure App Service for production use.

## 📋 Prerequisites

1. **Azure Account**: Sign up at [portal.azure.com](https://portal.azure.com)
2. **Azure CLI** (Optional): Download from [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Git**: Ensure Git is installed on your system

## 🎯 Deployment Methods

### Method 1: Azure Portal Deployment (Recommended for Beginners)

#### Step 1: Create Azure App Service

1. **Login to Azure Portal**
   - Go to [portal.azure.com](https://portal.azure.com)
   - Sign in with your Azure account

2. **Create Resource Group**
   - Click "Resource groups" → "Create"
   - Name: `cuet-analyzer-rg`
   - Region: Choose closest to your users (e.g., `East US`, `West Europe`)
   - Click "Review + create" → "Create"

3. **Create App Service**
   - Search for "App Services" → "Create"
   - **Basics:**
     - Subscription: Your subscription
     - Resource Group: `cuet-analyzer-rg`
     - Name: `cuet-analyzer-app` (must be globally unique)
     - Publish: `Code`
     - Runtime stack: `Python 3.11`
     - Operating System: `Linux`
     - Region: Same as resource group
   
   - **App Service Plan:**
     - Create new plan: `cuet-analyzer-plan`
     - SKU: `B1` (Basic) - $13/month
     - For testing: `F1` (Free) - No cost but limited
   
   - Click "Review + create" → "Create"

#### Step 2: Configure App Settings

1. **Navigate to Your App Service**
   - Go to your created App Service
   - In left menu, click "Configuration"

2. **Add Application Settings**
   ```
   WEBSITE_PORT = 8000
   SCM_DO_BUILD_DURING_DEPLOYMENT = true
   ENABLE_ORYX_BUILD = true
   ```

3. **Add Startup Command**
   - In Configuration, go to "General settings"
   - Startup Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000`
   - Save changes

#### Step 3: Deploy Your Code

1. **Enable Git Deployment**
   - Go to "Deployment Center"
   - Source: `Local Git`
   - Click "Save"
   - Copy the Git clone URL

2. **Push Your Code**
   ```bash
   # In your project directory
   git init
   git add .
   git commit -m "Initial deployment"
   
   # Add Azure as remote (replace URL with your App Service Git URL)
   git remote add azure https://your-app-name.scm.azurewebsites.net:443/your-app-name.git
   
   # Deploy
   git push azure main
   ```

3. **Deployment Credentials**
   - In Deployment Center, click "FTPS credentials"
   - Note down username/password for Git push

### Method 2: Azure CLI Deployment (Advanced)

#### Step 1: Install and Login
```bash
# Install Azure CLI
# Windows: Download from Microsoft website
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Set subscription (if multiple)
az account set --subscription "your-subscription-id"
```

#### Step 2: Create Resources
```bash
# Create resource group
az group create --name cuet-analyzer-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name cuet-analyzer-plan \
  --resource-group cuet-analyzer-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --name cuet-analyzer-app \
  --resource-group cuet-analyzer-rg \
  --plan cuet-analyzer-plan \
  --runtime "PYTHON|3.11"
```

#### Step 3: Configure and Deploy
```bash
# Set app settings
az webapp config appsettings set \
  --name cuet-analyzer-app \
  --resource-group cuet-analyzer-rg \
  --settings \
    WEBSITE_PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true

# Set startup command
az webapp config set \
  --name cuet-analyzer-app \
  --resource-group cuet-analyzer-rg \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000"

# Deploy from local Git
az webapp deployment source config-local-git \
  --name cuet-analyzer-app \
  --resource-group cuet-analyzer-rg

# Get deployment URL
az webapp deployment list-publishing-credentials \
  --name cuet-analyzer-app \
  --resource-group cuet-analyzer-rg
```

## 📁 File Structure for Deployment

Your project should have these files for Azure deployment:

```
du_admission_analyzer/
├── app.py                     # Main FastAPI application
├── requirements-azure.txt     # Azure-optimized dependencies
├── startup.txt               # Azure startup command
├── .env.azure                # Azure environment variables
├── pyproject.toml            # Build configuration
├── templates/
│   └── index.html            # Frontend template
├── data/                     # PDF files directory
├── outputs/                  # Generated analysis files
└── static/                   # Static assets (if any)
```

## 🔧 Configuration Files Explained

### requirements-azure.txt
Optimized dependencies for Azure App Service with pinned versions for stability.

### startup.txt
```
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

### .env.azure
Environment variables for Azure deployment:
```
PYTHONPATH=/home/site/wwwroot
ENVIRONMENT=production
DEBUG=false
```

### pyproject.toml
Build system configuration for Azure Oryx build system.

## 🚦 Post-Deployment Steps

### 1. Verify Deployment
- Visit: `https://your-app-name.azurewebsites.net`
- Check health: `https://your-app-name.azurewebsites.net/api/health`
- API docs: `https://your-app-name.azurewebsites.net/docs`

### 2. Upload Sample Data
1. Visit your deployed application
2. Use the upload feature to upload a PDF file
3. Verify that data processing works correctly

### 3. Monitor Application
- In Azure Portal, go to your App Service
- Check "Logs" → "App Service logs"
- Enable "Application Logging" for troubleshooting

## 🎨 Custom Domain (Optional)

### Add Custom Domain
1. In App Service, go to "Custom domains"
2. Click "Add custom domain"
3. Enter your domain name
4. Add DNS records as instructed
5. Bind SSL certificate for HTTPS

## 💰 Cost Estimation

### Basic Tier (B1)
- **Monthly Cost**: ~$13 USD
- **Features**: 
  - 1.75 GB RAM
  - 10 GB storage
  - Custom domains
  - SSL certificates
  - Auto-scaling (up to 3 instances)

### Free Tier (F1)
- **Monthly Cost**: Free
- **Limitations**:
  - 1 GB RAM
  - 1 GB storage
  - 60 minutes compute per day
  - No custom domains
  - No SSL certificates

## 🔍 Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Check startup command in Configuration
   - Verify `requirements-azure.txt` is present
   - Check Application logs

2. **Port Issues**
   - Ensure `WEBSITE_PORT=8000` is set
   - Verify app binds to `0.0.0.0:8000`

3. **File Upload Issues**
   - Azure App Service has limited write access
   - Files are stored in `/tmp` which is temporary
   - Consider Azure Blob Storage for persistence

4. **Build Failures**
   - Check build logs in Deployment Center
   - Verify `pyproject.toml` configuration
   - Ensure all dependencies are in `requirements-azure.txt`

### Debug Commands
```bash
# Check app logs
az webapp log tail --name cuet-analyzer-app --resource-group cuet-analyzer-rg

# SSH into container (for debugging)
az webapp ssh --name cuet-analyzer-app --resource-group cuet-analyzer-rg

# Restart app
az webapp restart --name cuet-analyzer-app --resource-group cuet-analyzer-rg
```

## 🔒 Security Considerations

1. **Environment Variables**: Store sensitive data in App Settings
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Configure appropriate CORS settings
4. **File Upload**: Validate and limit file uploads
5. **Rate Limiting**: Consider implementing rate limiting

## 📊 Monitoring and Analytics

### Azure Application Insights
1. Enable Application Insights in App Service
2. Monitor performance, errors, and usage
3. Set up alerts for critical issues

### Log Analytics
- Monitor application logs
- Set up custom queries
- Create dashboards

## 🚀 Next Steps

1. **Deploy** using your preferred method
2. **Test** all functionality thoroughly
3. **Monitor** application performance
4. **Scale** as needed based on usage
5. **Backup** important data regularly

## 📞 Support

- **Azure Documentation**: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Azure Support**: Available through Azure Portal

---

**🎉 Your CUET UG Admission Analyzer is now ready for the cloud!**

Access your application at: `https://your-app-name.azurewebsites.net`
