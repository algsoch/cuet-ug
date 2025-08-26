#!/usr/bin/env python3
"""
Test the complete pipeline with smart cleaner
"""

import sys
sys.path.insert(0, 'src')

from src.pipeline import DUAdmissionPipeline
import os

def test_complete_pipeline():
    """Test the complete pipeline with smart cleaner"""
    print("🚀 Testing Complete Pipeline with Smart Cleaner...")
    
    # Find the latest PDF file
    data_dir = "data"
    if os.path.exists(data_dir):
        pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
        if pdf_files:
            pdf_file = pdf_files[0]
            pdf_path = os.path.join(data_dir, pdf_file)
            print(f"📄 Processing PDF: {pdf_file}")
            
            # Run the pipeline
            pipeline = DUAdmissionPipeline()
            results = pipeline.process_pdf(pdf_path)
            
            if results and results.get('success'):
                print(f"\n🎉 Pipeline completed successfully!")
                print(f"📊 Results summary:")
                print(f"   Raw data rows: {len(pipeline.raw_data)}")
                print(f"   Clean data rows: {len(pipeline.clean_data)}")
                print(f"   Data efficiency: {(len(pipeline.clean_data)/len(pipeline.raw_data)*100):.1f}%")
                print(f"   Excel file: {results['files']['excel']}")
                print(f"   CSV file: {results['files']['csv']}")
                
                # Check analytics
                if 'analytics' in results:
                    analytics = results['analytics']
                    overview = analytics.get('overview', {})
                    print(f"\n📈 Analytics Overview:")
                    print(f"   Total colleges: {overview.get('total_colleges', 'N/A')}")
                    print(f"   Total programs: {overview.get('total_programs', 'N/A')}")
                    print(f"   Total seats: {overview.get('total_seats', 'N/A')}")
                
                return True
            else:
                print(f"❌ Pipeline failed: {results.get('error', 'Unknown error')}")
                return False
        else:
            print("❌ No PDF files found in data directory")
            return False
    else:
        print("❌ Data directory not found")
        return False

if __name__ == "__main__":
    success = test_complete_pipeline()
    if success:
        print("\n✅ Complete pipeline test successful!")
    else:
        print("\n❌ Pipeline test failed!")
