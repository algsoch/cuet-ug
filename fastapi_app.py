"""
FastAPI Application Template for DU Admission Analyzer
Ready-to-use web API for PDF processing
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import tempfile
import os
import shutil
from datetime import datetime
from typing import Dict, Any
import uvicorn

# Import our pipeline
import sys
sys.path.insert(0, 'src')
from src.pipeline import process_admission_pdf

# Initialize FastAPI app
app = FastAPI(
    title="DU Admission Analyzer API",
    description="Extract, clean, analyze, and export Delhi University admission data from PDFs",
    version="1.0.0"
)

# Create outputs directory if it doesn't exist
os.makedirs("outputs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# Serve static files (for downloading results)
app.mount("/downloads", StaticFiles(directory="outputs"), name="downloads")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Welcome page with API documentation"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DU Admission Analyzer API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            .feature { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .endpoint { background: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #27ae60; }
            code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 DU Admission Analyzer API</h1>
            
            <p>A comprehensive API for extracting, cleaning, analyzing, and exporting Delhi University admission data from PDF files.</p>
            
            <h2>🌟 Features</h2>
            <div class="feature">📄 <strong>PDF Extraction:</strong> Extract tables from DU admission PDFs</div>
            <div class="feature">🧹 <strong>Data Cleaning:</strong> Handle split rows, column alignment, and data normalization</div>
            <div class="feature">📊 <strong>Analytics:</strong> Generate comprehensive insights and statistics</div>
            <div class="feature">📤 <strong>Excel Export:</strong> Multi-sheet Excel files with formatting</div>
            <div class="feature">🔄 <strong>Batch Processing:</strong> Process multiple PDFs simultaneously</div>
            
            <h2>🔌 API Endpoints</h2>
            
            <div class="endpoint">
                <strong>POST /upload</strong><br>
                Upload and process a PDF file<br>
                <code>curl -X POST -F "file=@yourfile.pdf" http://localhost:8000/upload</code>
            </div>
            
            <div class="endpoint">
                <strong>POST /process-url</strong><br>
                Process a PDF from URL<br>
                <code>curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/file.pdf"}' http://localhost:8000/process-url</code>
            </div>
            
            <div class="endpoint">
                <strong>GET /download/{filename}</strong><br>
                Download processed files<br>
                <code>http://localhost:8000/download/analysis_20231225_123456.xlsx</code>
            </div>
            
            <div class="endpoint">
                <strong>GET /docs</strong><br>
                Interactive API documentation (Swagger UI)<br>
                <code>http://localhost:8000/docs</code>
            </div>
            
            <h2>🚀 Quick Start</h2>
            <ol>
                <li>Upload a PDF using the <code>/upload</code> endpoint</li>
                <li>Receive processing results with download links</li>
                <li>Download your Excel and CSV files</li>
            </ol>
            
            <p><a href="/docs" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📚 View Interactive API Docs</a></p>
        </div>
    </body>
    </html>
    """
    return html_content


@app.post("/upload")
async def upload_and_process(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and process a PDF file
    
    Args:
        file: PDF file to process
        
    Returns:
        Processing results with download links
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file temporarily
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"upload_{timestamp}_{file.filename}"
    temp_path = os.path.join("uploads", temp_filename)
    
    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the PDF
        results = process_admission_pdf(
            temp_path,
            output_dir="outputs",
            export_filename=f"analysis_{timestamp}.xlsx"
        )
        
        if results['success']:
            # Get filenames for download links
            excel_filename = os.path.basename(results['files']['excel'])
            csv_filename = os.path.basename(results['files']['csv'])
            
            return {
                "status": "success",
                "message": "PDF processed successfully",
                "data": {
                    "rows_processed": results['data_shape'][0],
                    "columns": results['data_shape'][1],
                    "total_seats": results['analytics']['overview']['total_seats'],
                    "total_colleges": results['analytics']['overview']['total_colleges'],
                    "total_programs": results['analytics']['overview']['total_programs']
                },
                "insights": results['analytics']['insights'][:3],  # Top 3 insights
                "downloads": {
                    "excel": f"/downloads/{excel_filename}",
                    "csv": f"/downloads/{csv_filename}"
                },
                "processing_time": results['summary']['processing_timestamp']
            }
        else:
            raise HTTPException(status_code=500, detail=f"Processing failed: {results['error']}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/process-url")
async def process_from_url(request: Dict[str, str]) -> Dict[str, Any]:
    """
    Process a PDF from URL
    
    Args:
        request: JSON with 'url' field containing PDF URL
        
    Returns:
        Processing results with download links
    """
    url = request.get('url')
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Process the PDF directly from URL
        results = process_admission_pdf(
            url,
            output_dir="outputs",
            export_filename=f"url_analysis_{timestamp}.xlsx"
        )
        
        if results['success']:
            # Get filenames for download links
            excel_filename = os.path.basename(results['files']['excel'])
            csv_filename = os.path.basename(results['files']['csv'])
            
            return {
                "status": "success",
                "message": "PDF processed successfully from URL",
                "source_url": url,
                "data": {
                    "rows_processed": results['data_shape'][0],
                    "columns": results['data_shape'][1],
                    "total_seats": results['analytics']['overview']['total_seats'],
                    "total_colleges": results['analytics']['overview']['total_colleges'],
                    "total_programs": results['analytics']['overview']['total_programs']
                },
                "insights": results['analytics']['insights'][:3],
                "downloads": {
                    "excel": f"/downloads/{excel_filename}",
                    "csv": f"/downloads/{csv_filename}"
                },
                "processing_time": results['summary']['processing_timestamp']
            }
        else:
            raise HTTPException(status_code=500, detail=f"Processing failed: {results['error']}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a processed file
    
    Args:
        filename: Name of the file to download
        
    Returns:
        File download response
    """
    file_path = os.path.join("outputs", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "DU Admission Analyzer API"
    }


@app.get("/stats")
async def get_processing_stats():
    """Get processing statistics"""
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        return {"files_processed": 0, "total_files": 0}
    
    files = os.listdir(outputs_dir)
    excel_files = [f for f in files if f.endswith('.xlsx')]
    csv_files = [f for f in files if f.endswith('.csv')]
    
    return {
        "files_processed": len(excel_files),
        "total_files": len(files),
        "excel_files": len(excel_files),
        "csv_files": len(csv_files),
        "last_processed": max([os.path.getctime(os.path.join(outputs_dir, f)) for f in files]) if files else None
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "status_code": 404}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "status_code": 500}


if __name__ == "__main__":
    print("🚀 Starting DU Admission Analyzer API...")
    print("📚 Interactive docs: http://localhost:8000/docs")
    print("🏠 Home page: http://localhost:8000/")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )
