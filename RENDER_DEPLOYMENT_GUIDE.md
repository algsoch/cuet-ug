# 🚀 CUET UG Admission Analyzer - Render Deployment Guide

## Why Render?

Render is a modern cloud platform that's simpler than AWS/Azure and offers:
- ✅ **Free Tier Available** - Perfect for testing and small projects
- ✅ **Automatic Deployments** - Deploy on every git push
- ✅ **Built-in SSL/HTTPS** - Secure by default
- ✅ **No Configuration Hassle** - Just connect your Git repo
- ✅ **Docker Support** - Deploy containers easily
- ✅ **Fast Global CDN** - Great performance worldwide

## 🎯 Deployment Options

### Option 1: Direct Git Deployment (Recommended)
Deploy directly from your GitHub repository - easiest method!

### Option 2: Docker Deployment
Deploy using the Docker container we've created.

---

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free)
3. **Git Repository** - Push your code to GitHub

---

## 🚀 Method 1: Direct Git Deployment

### Step 1: Prepare Your Code

1. **Create a GitHub repository** (if you haven't already)
2. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "CUET Admission Analyzer for Render deployment"
   git branch -M main
   git remote add origin https://github.com/yourusername/cuet-admission-analyzer.git
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository:**
   - Choose "Connect a repository"
   - Select your GitHub account
   - Choose the repository with your CUET analyzer
4. **Configure the service:**
   ```
   Name: cuet-admission-analyzer
   Region: Oregon (US West) or Frankfurt (Europe)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python -m uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
5. **Choose your plan:**
   - **Free**: $0/month (good for testing, sleeps after 15 min of inactivity)
   - **Starter**: $7/month (always on, custom domains)
6. **Click "Create Web Service"**

### Step 3: Environment Variables (Optional)

In your Render dashboard:
1. Go to your service
2. Click "Environment"
3. Add any environment variables you need:
   ```
   ENVIRONMENT = production
   PYTHONPATH = /opt/render/project/src
   ```

### Step 4: Wait for Deployment

- Render will automatically build and deploy your app
- This usually takes 3-5 minutes
- You'll get a live URL like: `https://cuet-admission-analyzer.onrender.com`

---

## 🐳 Method 2: Docker Deployment

### Step 1: Prepare Docker Image

1. **Build locally (optional, for testing):**
   ```bash
   docker build -t cuet-analyzer .
   docker run -p 8000:8000 cuet-analyzer
   ```

2. **Test locally:**
   - Visit `http://localhost:8000`
   - Verify everything works

### Step 2: Deploy Docker on Render

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +" → "Web Service"**
3. **Choose "Deploy an existing image from a registry"**
4. **Build from repository:**
   - Connect your GitHub repository
   - Set Dockerfile path: `./Dockerfile`
5. **Configure:**
   ```
   Name: cuet-admission-analyzer-docker
   Region: Oregon or Frankfurt
   Instance Type: Free (or Starter for production)
   ```
6. **Click "Create Web Service"**

---

## ⚙️ Configuration Files Explained

### `render.yaml` (Optional)
Infrastructure as code for Render - defines your service configuration.

### `Dockerfile`
Containerizes your application for consistent deployment across any platform.

### `docker-compose.yml`
For local development with Docker - makes it easy to run everything locally.

### `requirements.txt`
Optimized dependencies for cloud deployment - removed heavy packages that aren't needed.

---

## 🔧 Post-Deployment Steps

### 1. Verify Your Deployment

Visit your Render URL (something like `https://your-app-name.onrender.com`):

- ✅ Main page loads
- ✅ Health check works: `/api/health`
- ✅ API docs accessible: `/docs`

### 2. Test Core Functionality

1. **Upload a PDF file**
2. **Verify data processing works**
3. **Check all interactive features:**
   - Pagination toggle
   - Search functionality
   - Table sorting
   - Charts and analysis

### 3. Monitor Your App

- Check Render dashboard for logs
- Monitor performance and errors
- Set up alerts if needed

---

## 🎨 Custom Domain (Optional)

### For Starter Plan and Above:

1. **In Render dashboard:**
   - Go to your service
   - Click "Settings" → "Custom Domains"
   - Add your domain (e.g., `cuet-analyzer.yourdomain.com`)

2. **Configure DNS:**
   - Add CNAME record pointing to your Render URL
   - SSL certificate is automatically provided

---

## 💰 Pricing Comparison

### Free Tier
- **Cost**: $0/month
- **Limitations**: 
  - Sleeps after 15 minutes of inactivity
  - 512MB RAM
  - Shared CPU
  - 750 hours/month limit

### Starter Plan
- **Cost**: $7/month
- **Features**:
  - Always on (no sleeping)
  - 512MB RAM
  - Custom domains
  - Unlimited hours

### Standard Plan
- **Cost**: $25/month
- **Features**:
  - 2GB RAM
  - Faster CPUs
  - Priority support

---

## 🔄 Automatic Deployments

Render automatically deploys when you push to your main branch:

```bash
# Make changes to your code
git add .
git commit -m "Update analysis features"
git push origin main
# Render automatically deploys your changes!
```

---

## 🐳 Local Docker Development

Run your app locally with Docker:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run with plain Docker
docker build -t cuet-analyzer .
docker run -p 8000:8000 cuet-analyzer

# Access your app at http://localhost:8000
```

---

## 🔍 Troubleshooting

### Common Issues:

1. **Build fails:**
   - Check `requirements.txt` for compatibility
   - Verify Python version (should be 3.11)
   - Check build logs in Render dashboard

2. **App doesn't start:**
   - Verify start command: `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Check if `app.py` exists in root directory
   - Review runtime logs

3. **Features don't work:**
   - Test locally first with Docker
   - Check browser console for errors
   - Verify all static files are served correctly

4. **File uploads fail:**
   - Render has filesystem limitations
   - Files are temporary (cleared on restart)
   - Consider adding cloud storage for production

### Debug Commands:

```bash
# Check Docker build locally
docker build -t cuet-analyzer .

# Run and debug
docker run -it cuet-analyzer /bin/bash

# Check logs in Render dashboard
# No CLI needed - use web interface
```

---

## 🚀 Next Steps

1. **Deploy to Render** using your preferred method
2. **Test thoroughly** with real PDF files
3. **Share your URL** - your app is now live!
4. **Monitor performance** in Render dashboard
5. **Scale up** to paid plan if needed

---

## 📞 Support Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Docker Documentation**: [docs.docker.com](https://docs.docker.com)

---

## 🎉 Success Metrics

After deployment, you should have:

✅ **Live URL**: `https://your-app-name.onrender.com`
✅ **Automatic deployments** on git push
✅ **Free HTTPS/SSL** certificate
✅ **Global CDN** for fast loading
✅ **Docker containerization** for portability
✅ **Professional cloud hosting** for your analyzer

**Your CUET UG Admission Analyzer is now live on the internet! 🚀**
