#!/usr/bin/env python3

import sys
import os
import asyncio
import traceback
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import process_admission_pdf

# Simulate the background processing function from app.py
processing_status = {}

async def process_file_background(file_path: str, process_id: str, output_filename: str):
    """Background task for processing files - copied from app.py"""
    try:
        # Update status
        processing_status[process_id] = processing_status.get(process_id, {})
        processing_status[process_id].update({
            "status": "processing",
            "progress": 20,
            "message": "Extracting data from PDF..."
        })
        
        print(f"🔄 Starting background processing: {file_path}")
        print(f"📂 Output filename: {output_filename}")
        print(f"🆔 Process ID: {process_id}")
        
        # Process the file
        results = process_admission_pdf(file_path, "outputs", output_filename)
        
        print(f"📊 Processing results: {results['success']}")
        
        if results['success']:
            print("✅ Background processing completed successfully!")
            # Update status
            processing_status[process_id].update({
                "status": "completed",
                "progress": 100,
                "message": "Processing completed successfully",
                "results": results,
                "end_time": datetime.now().isoformat()
            })
        else:
            print(f"❌ Background processing failed: {results['error']}")
            processing_status[process_id].update({
                "status": "error",
                "progress": 0,
                "message": f"Processing failed: {results['error']}",
                "error": results['error']
            })
    
    except Exception as e:
        print(f"💥 Exception in background processing: {str(e)}")
        traceback.print_exc()
        processing_status[process_id].update({
            "status": "error",
            "progress": 0,
            "message": f"Processing error: {str(e)}",
            "error": str(e)
        })

async def debug_background_processing():
    """Debug the background processing function"""
    print("🔍 Debugging Background Processing Function")
    print("=" * 60)
    
    # Use the uploaded file
    file_path = "uploads/upload_20250826_122442_test_file.pdf"
    process_id = "debug_background_20250826"
    output_filename = "debug_background_output.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Initialize processing status
    processing_status[process_id] = {
        "status": "starting",
        "progress": 0,
        "message": "Starting processing...",
        "start_time": datetime.now().isoformat()
    }
    
    # Run the background processing function
    await process_file_background(file_path, process_id, output_filename)
    
    # Check final status
    print("\n📋 Final Processing Status:")
    print(f"   Status: {processing_status[process_id]['status']}")
    print(f"   Message: {processing_status[process_id]['message']}")
    if 'error' in processing_status[process_id]:
        print(f"   Error: {processing_status[process_id]['error']}")

if __name__ == "__main__":
    asyncio.run(debug_background_processing())
