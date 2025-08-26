#!/usr/bin/env python3

import sys
import os
import pandas as pd
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import process_admission_pdf

def debug_excel_export():
    """Debug the exact error during Excel export"""
    print("🔍 Debugging Excel Export Error")
    print("=" * 50)
    
    try:
        # Use the same test file
        test_file = "test_file.pdf"
        
        if not os.path.exists(test_file):
            print(f"❌ Test file {test_file} not found")
            return
        
        print(f"📄 Processing: {test_file}")
        
        # Try to process the PDF
        results = process_admission_pdf(test_file, "outputs", "debug_test.xlsx")
        
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
    debug_excel_export()
