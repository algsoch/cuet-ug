# 🚀 QUICK START: Deploy Your CUET UG Admission Analyzer

## 🎯 Choose Your Deployment Method

### Option 1: 🌐 Render (Cloud) - Live Web App
**Perfect for**: Sharing with others, production use
**Time**: 5 minutes | **Cost**: Free tier available

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "CUET Analyzer ready for deployment"
   git remote add origin https://github.com/yourusername/cuet-analyzer.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com) → Sign up (free)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     ```
     Build Command: pip install -r requirements.txt
     Start Command: python -m uvicorn app:app --host 0.0.0.0 --port $PORT
     ```
   - Click "Create Web Service"

3. **Done!** Your app will be live at: `https://your-app-name.onrender.com`

---

### Option 2: 🐳 Docker (Local) - Development & Testing
**Perfect for**: Local development, offline use
**Time**: 2 minutes | **Cost**: Free

#### Windows (Easy):
```cmd
deploy-docker.bat
```

#### Windows PowerShell:
```powershell
.\deploy-docker.ps1
```

#### Docker Compose (All Systems):
```bash
docker-compose up --build
```

**Access locally**: `http://localhost:8000`

---

## 📋 Prerequisites

### For Render:
- [x] GitHub account
- [x] Render account (free at render.com)

### For Docker:
- [x] Docker Desktop installed
- [x] Docker Desktop running

---

## 🔧 What You Get

After deployment, your analyzer includes:

✅ **PDF Upload & Processing** - Upload CUET admission PDFs
✅ **Interactive Data Table** - 1528 admission records
✅ **Smart Pagination** - Toggle between 70 rows ↔ all rows  
✅ **Advanced Search** - Search with highlighting
✅ **Complete Sorting** - Sort all table columns
✅ **Full Text Display** - No truncation of college/program names
✅ **Trend Analysis** - Charts and visualizations
✅ **Responsive Design** - Works on mobile/tablet
✅ **Professional UI** - Bootstrap-based interface

---

## 🧪 Test Your Deployment

1. **Upload a PDF** - Test with a CUET admission PDF file
2. **Check data** - Verify 66 colleges, 258 programs display correctly
3. **Test features** - Try search, sorting, pagination
4. **View analysis** - Check charts and trend analysis work

---

## 💡 Pro Tips

### Render Deployment:
- **Free tier** puts app to sleep after 15 minutes of inactivity
- **Starter plan** ($7/month) keeps app always on
- **Custom domains** available on paid plans
- **Auto-deploys** on every git push to main branch

### Docker Deployment:
- **Data persists** across container restarts
- **Easy scaling** with docker-compose
- **Perfect for development** and testing
- **Run anywhere** Docker is supported

---

## 🆘 Quick Troubleshooting

### Render Issues:
- **Build fails**: Check `requirements.txt` has all dependencies
- **App won't start**: Verify start command in Render dashboard
- **Slow loading**: App might be sleeping (free tier)

### Docker Issues:
- **Build fails**: Make sure Docker Desktop is running
- **Port busy**: Try different port with `-p 8001:8000`
- **Permission errors**: Run as administrator (Windows)

---

## 📞 Need Help?

- **Render Guide**: `RENDER_DEPLOYMENT_GUIDE.md`
- **Docker Guide**: `DEPLOYMENT_GUIDE.md`
- **Complete Instructions**: `DEPLOYMENT_CHECKLIST.md`

---

## 🎉 Success!

Your **CUET UG Admission Analyzer** is now deployed! 

**Render URL**: `https://your-app-name.onrender.com`  
**Docker URL**: `http://localhost:8000`

**Share your analyzer and help students make informed admission decisions! 🎓**
