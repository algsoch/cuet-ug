"""
Simple test script to verify the DU Admission Analyzer works correctly
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules import correctly"""
    try:
        from src.pipeline import process_admission_pdf
        from src.pdf_extractor import extract_pdf
        from src.data_cleaner import clean_data
        from src.analytics import generate_analytics_summary
        from src.excel_exporter import export_to_excel
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_with_sample_data():
    """Test with sample data (without PDF)"""
    try:
        import pandas as pd
        from src.data_cleaner import clean_data
        from src.analytics import generate_analytics_summary
        from src.excel_exporter import export_to_excel
        
        # Create sample data
        sample_data = pd.DataFrame({
            'S.NO.': [1, 2, 3],
            'NAME OF THE COLLEGE': ['Test College A', 'Test College B', 'Test College C'],
            'NAME OF THE PROGRAM': ['B.A. English', 'B.Sc. Mathematics', 'B.Com.'],
            'UR': [10, 15, 20],
            'OBC': [5, 8, 10],
            'SC': [3, 4, 5],
            'ST': [2, 2, 3],
            'EWS': [1, 2, 2],
            'SIKH': [1, 1, 1],
            'PwBD': [1, 1, 1]
        })
        
        print("📊 Testing with sample data...")
        
        # Test cleaning (should pass through since data is already clean)
        clean_df = clean_data(sample_data)
        print(f"✅ Data cleaning: {len(clean_df)} rows")
        
        # Test analytics
        analytics = generate_analytics_summary(clean_df)
        print(f"✅ Analytics generated: {analytics['overview']['total_seats']} total seats")
        
        # Test Excel export
        excel_path = export_to_excel(clean_df, "test_output.xlsx", "outputs")
        print(f"✅ Excel exported: {excel_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running DU Admission Analyzer Tests...")
    print("=" * 50)
    
    # Test 1: Imports
    print("\n1. Testing imports...")
    import_success = test_imports()
    
    # Test 2: Sample data processing
    print("\n2. Testing with sample data...")
    sample_success = test_with_sample_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"   Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   Sample Processing: {'✅ PASS' if sample_success else '❌ FAIL'}")
    
    if import_success and sample_success:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main.py <pdf_url_or_path>")
        print("2. Or open demo_notebook.ipynb for interactive usage")
        print("3. Check the outputs/ folder for generated files")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
