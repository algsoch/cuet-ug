# 🚀 Quick Azure Deployment Steps for CUET UG Admission Analyzer

## Option 1: Using PowerShell Script (Recommended)

1. **Open PowerShell as Administrator**
2. **Navigate to your project directory:**
   ```powershell
   cd "C:\Users\npdim\OneDrive\Desktop\cuet ug\du_admission_analyzer"
   ```

3. **Run the deployment script:**
   ```powershell
   .\deploy-to-azure.ps1 -AppName "your-unique-app-name"
   ```
   Replace `your-unique-app-name` with a globally unique name (e.g., `cuet-analyzer-yourname`)

4. **Follow the prompts:**
   - Login to Azure when prompted
   - Wait for deployment to complete
   - Open the URL when deployment finishes

## Option 2: Using Batch File (Windows)

1. **Open Command Prompt**
2. **Navigate to your project directory:**
   ```cmd
   cd "C:\Users\npdim\OneDrive\Desktop\cuet ug\du_admission_analyzer"
   ```

3. **Run the batch file:**
   ```cmd
   deploy-to-azure.bat
   ```

4. **Follow the prompts:**
   - Enter a unique app name when asked
   - Login to Azure when prompted
   - Wait for deployment to complete

## Option 3: Manual Azure Portal Steps

### Step 1: Create App Service in Azure Portal

1. **Go to [portal.azure.com](https://portal.azure.com)**
2. **Click "Create a resource"**
3. **Search for "Web App" and click "Create"**
4. **Fill in the details:**
   - **Subscription:** Your Azure subscription
   - **Resource Group:** Create new → `cuet-analyzer-rg`
   - **Name:** `your-unique-app-name` (globally unique)
   - **Publish:** Code
   - **Runtime stack:** Python 3.11
   - **Operating System:** Linux
   - **Region:** East US (or closest to you)
   - **App Service Plan:** Create new → Basic B1 ($13/month)

5. **Click "Review + Create" → "Create"**

### Step 2: Configure App Settings

1. **Go to your App Service in Azure Portal**
2. **Click "Configuration" in the left menu**
3. **Add these Application Settings:**
   - `WEBSITE_PORT` = `8000`
   - `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
   - `ENABLE_ORYX_BUILD` = `true`

4. **Go to "General settings" tab**
5. **Set Startup Command:**
   ```
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
   ```

6. **Click "Save"**

### Step 3: Deploy Your Code

1. **Go to "Deployment Center" in your App Service**
2. **Choose "Local Git" as source**
3. **Copy the Git clone URL**
4. **In your project directory, run:**
   ```cmd
   git init
   git add .
   git commit -m "Initial deployment"
   git remote add azure [paste-your-git-url-here]
   git push azure main
   ```

## 🎯 Expected Results

After successful deployment, you should be able to access:

- **Main Application:** `https://your-app-name.azurewebsites.net`
- **Health Check:** `https://your-app-name.azurewebsites.net/api/health`
- **API Documentation:** `https://your-app-name.azurewebsites.net/docs`

## 🔧 Testing Your Deployment

1. **Visit your application URL**
2. **Click "Upload PDF" button**
3. **Upload a CUET admission PDF file**
4. **Verify that:**
   - Data is processed correctly
   - Tables display with pagination
   - Search functionality works
   - Charts and analysis are shown

## 🆘 Troubleshooting

### If deployment fails:
1. Check Azure Portal → Your App Service → Logs
2. Look for error messages in deployment logs
3. Verify all required files are present
4. Check if app name is globally unique

### If app doesn't start:
1. Check Application Settings are configured correctly
2. Verify startup command is set
3. Look at runtime logs in Azure Portal

### If features don't work:
1. Check browser console for JavaScript errors
2. Verify API endpoints are accessible
3. Check if file uploads are working

## 💰 Cost Information

- **Free Tier (F1):** $0/month (limited features, 60 min/day)
- **Basic Tier (B1):** ~$13/month (recommended for production)
- **Standard Tier (S1):** ~$56/month (auto-scaling, staging slots)

## 📞 Support

If you encounter issues:
1. Check the full deployment guide: `AZURE_DEPLOYMENT_GUIDE.md`
2. Visit Azure documentation: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
3. Check FastAPI documentation: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

**🎉 Congratulations! Your CUET UG Admission Analyzer is now live on Azure!**
