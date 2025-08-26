#!/usr/bin/env python3

import sys
import os
import pandas as pd
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import process_admission_pdf

def debug_uploaded_file():
    """Debug processing uploaded file directly"""
    print("🔍 Debugging Uploaded File Processing")
    print("=" * 50)
    
    try:
        # Use one of the uploaded files
        uploaded_file = "uploads/upload_20250826_122442_test_file.pdf"
        
        if not os.path.exists(uploaded_file):
            print(f"❌ Uploaded file {uploaded_file} not found")
            return
        
        print(f"📄 Processing uploaded file: {uploaded_file}")
        
        # Try to process the uploaded PDF
        results = process_admission_pdf(uploaded_file, "outputs", "debug_uploaded.xlsx")
        
        if results['success']:
            print("✅ Processing completed successfully!")
            print(f"📊 Analytics: {len(results['analytics'])} sections")
            print(f"📁 Files: {results['files']}")
        else:
            print(f"❌ Processing failed!")
            print(f"🔍 Error: {results['error']}")
            print(f"📍 Stage: {results['stage']}")
            
    except Exception as e:
        print(f"💥 Exception occurred: {str(e)}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_uploaded_file()
