# 🔧 Render Deployment Troubleshooting Guide

## ✅ Problem Fixed: Tabula Dependency Issue

**Issue**: The deployment was failing with `ModuleNotFoundError: No module named 'tabula'`

**Root Cause**: The `tabula-py` library requires Java runtime, which is not available in Render's Python runtime environment.

**Solution Applied**: 
- ✅ Made tabula import optional in `src/pdf_extractor.py`
- ✅ Updated PDF extraction to use `pdfplumber` only (no Java required)
- ✅ Optimized `requirements.txt` for cloud deployment
- ✅ Updated Dockerfile for better compatibility

---

## 🚀 Current Status

Your CUET UG Admission Analyzer is now **Render-ready** with:

### ✅ Cloud-Optimized PDF Processing
- **Primary**: `pdfplumber` (pure Python, no Java)
- **Backup**: `PyPDF2` and `pypdfium2`
- **Robust**: Multiple extraction methods for different PDF formats

### ✅ Fixed Dependencies
- Removed Java-dependent libraries
- Added `pdfminer.six` for additional PDF support
- Optimized for Render's Python 3.11 environment

---

## 🎯 Deployment Status Check

After the latest push, Render should automatically redeploy. You can check:

1. **Render Dashboard**: Go to your service and check build logs
2. **Build Success**: Look for "Build successful" message
3. **Deploy Success**: Check for "Deploy successful" message
4. **Live URL**: Visit your app URL to verify it's working

---

## 🧪 Testing Your Fixed Deployment

Once deployment succeeds:

### 1. Basic Health Check
- ✅ Visit: `https://your-app-name.onrender.com/api/health`
- ✅ Should return: `{"status": "healthy", ...}`

### 2. Main Application
- ✅ Visit: `https://your-app-name.onrender.com`
- ✅ Should load the analyzer interface

### 3. PDF Upload Test
- ✅ Try uploading a PDF file
- ✅ Verify data processing works (using pdfplumber)

---

## 🔄 What Changed in the Fix

### File: `src/pdf_extractor.py`
```python
# Before (causing error):
from tabula.io import read_pdf

# After (graceful handling):
try:
    from tabula.io import read_pdf
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    read_pdf = None
```

### File: `requirements.txt`
```python
# Removed: tabula-py (requires Java)
# Added: pdfminer.six (pure Python)
# Kept: pdfplumber, PyPDF2, pypdfium2
```

---

## 📊 Expected Performance

### PDF Processing Methods (in order of preference):
1. **pdfplumber**: Main extraction method (works with most PDFs)
2. **pypdfium2**: Backup method for complex layouts
3. **PyPDF2**: Fallback for simple text extraction
4. **pdfminer.six**: Additional support for difficult PDFs

### Processing Time:
- **Small PDFs** (< 5MB): 10-30 seconds
- **Large PDFs** (> 5MB): 30-60 seconds
- **First upload**: Longer due to cold start (free tier)

---

## 🚨 Common Render Deployment Issues

### 1. Build Timeout
**Symptom**: Build fails after 15 minutes
**Solution**: Optimize dependencies, remove heavy packages

### 2. Memory Issues
**Symptom**: App crashes during PDF processing
**Solution**: Upgrade to Starter plan ($7/month) for more RAM

### 3. Cold Start Delays
**Symptom**: First request is very slow (free tier)
**Solution**: Upgrade to Starter plan for always-on service

### 4. File Storage Limitations
**Symptom**: Uploaded files disappear after restart
**Solution**: Files are temporary on Render (expected behavior)

---

## 🎛️ Render Configuration Summary

### Environment Variables (automatically set):
```
PORT = (set by Render)
PYTHONPATH = /opt/render/project/src
```

### Build Command:
```bash
pip install -r requirements.txt
```

### Start Command:
```bash
python -m uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

## 🔍 Debugging Steps

### If deployment still fails:

1. **Check Build Logs**:
   - Go to Render dashboard
   - Click on your service
   - Check "Events" tab for build logs

2. **Common Error Patterns**:
   ```
   ModuleNotFoundError → Missing dependency
   ImportError → Package compatibility issue
   Memory error → Need more RAM (upgrade plan)
   Timeout → Build taking too long
   ```

3. **Local Testing**:
   ```bash
   # Test locally first
   docker build -t cuet-analyzer .
   docker run -p 8000:8000 cuet-analyzer
   ```

### If app starts but features don't work:

1. **Check Runtime Logs** in Render dashboard
2. **Test API endpoints**:
   - `/api/health` - Basic health check
   - `/api/raw-data` - Data availability
   - `/docs` - API documentation

3. **Browser Console**: Check for JavaScript errors

---

## 💡 Optimization Tips

### For Better Performance:
1. **Upgrade to Starter Plan** ($7/month)
   - Always-on (no cold starts)
   - More RAM and CPU
   - Faster processing

2. **Optimize PDF Files**:
   - Smaller files process faster
   - Clear, tabular PDFs work best
   - Avoid scanned images

3. **Use Caching**:
   - App already includes result caching
   - Repeated processing is faster

---

## 🎉 Success Indicators

Your deployment is successful when:

✅ **Build completes** without errors
✅ **App starts** and responds to health check
✅ **Main page loads** with upload interface
✅ **PDF upload works** and processes data
✅ **Data displays** in tables with all features
✅ **Interactive features work** (search, sort, pagination)

---

## 📞 Still Need Help?

### Resources:
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **pdfplumber Docs**: [github.com/jsvine/pdfplumber](https://github.com/jsvine/pdfplumber)

### Quick Support:
1. Check Render dashboard logs first
2. Test locally with Docker
3. Verify PDF format compatibility
4. Consider upgrading plan for better performance

---

**🚀 Your CUET UG Admission Analyzer should now deploy successfully on Render!**
