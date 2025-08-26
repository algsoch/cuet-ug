"""
Test script to verify PDF processing with enhanced analytics
"""

import requests
import json
import time
import os

def test_pdf_processing():
    """Test PDF upload and processing with enhanced analytics"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing PDF Processing with Enhanced Analytics...")
    
    # Check if we have a test PDF file
    test_files = [
        "test_file.pdf",
        "25082025_VacantSeats_UG_Spot_Round.pdf",
        "test.pdf", 
        "sample.pdf"
    ]
    
    pdf_file = None
    for filename in test_files:
        if os.path.exists(filename):
            pdf_file = filename
            break
    
    if not pdf_file:
        print("📄 No test PDF file found in current directory")
        print("   Available files:", [f for f in os.listdir('.') if f.endswith('.pdf')])
        return False
    
    print(f"📄 Using test file: {pdf_file}")
    
    try:
        # Upload PDF file
        print("📤 Uploading PDF file...")
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file, f, 'application/pdf')}
            response = requests.post(f"{base_url}/api/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        process_id = result.get('process_id')
        
        if not process_id:
            print("❌ No process_id returned from upload")
            return False
        
        print(f"✅ Upload successful! Process ID: {process_id}")
        
        # Wait for processing to complete
        print("⏳ Waiting for processing to complete...")
        max_wait = 60  # Maximum wait time in seconds
        wait_time = 0
        
        while wait_time < max_wait:
            status_response = requests.get(f"{base_url}/api/status/{process_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                print(f"📊 Status: {status}")
                
                if status == 'completed':
                    print("✅ Processing completed successfully!")
                    
                    # Test the advanced analytics endpoint
                    print("🔍 Testing advanced analytics endpoint...")
                    analytics_response = requests.get(f"{base_url}/api/advanced-analytics/{process_id}")
                    
                    if analytics_response.status_code == 200:
                        analytics_data = analytics_response.json()
                        print("🎉 Advanced analytics generated successfully!")
                        
                        if 'data' in analytics_data:
                            data = analytics_data['data']
                            overview = data.get('overview', {})
                            
                            print(f"📈 Total Colleges: {overview.get('total_colleges', 'N/A')}")
                            print(f"📚 Total Programs: {overview.get('total_programs', 'N/A')}")
                            print(f"🪑 Total Seats: {overview.get('total_seats', 'N/A')}")
                            
                            categories = overview.get('categories', {})
                            if categories:
                                print("🏷️ Category Breakdown:")
                                for cat, count in categories.items():
                                    print(f"   {cat}: {count:,}")
                            
                            insights = data.get('insights', [])
                            if insights:
                                print(f"💡 Generated {len(insights)} insights")
                                for i, insight in enumerate(insights[:3]):  # Show first 3
                                    if isinstance(insight, dict):
                                        title = insight.get('title', f'Insight {i+1}')
                                        desc = insight.get('description', '')
                                        print(f"   {title}: {desc}")
                                    else:
                                        print(f"   {insight}")
                        
                        return True
                    else:
                        print(f"❌ Advanced analytics failed: {analytics_response.status_code}")
                        print(f"Response: {analytics_response.text}")
                        return False
                        
                elif status == 'failed':
                    print("❌ Processing failed")
                    print(f"Error: {status_data.get('error', 'Unknown error')}")
                    return False
                elif status == 'processing':
                    print("⏳ Still processing...")
                    time.sleep(5)
                    wait_time += 5
                else:
                    print(f"🤔 Unknown status: {status}")
                    time.sleep(2)
                    wait_time += 2
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
        
        print("⏰ Processing timeout reached")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DU Admission Analyzer - Enhanced PDF Processing Test")
    print("=" * 60)
    
    success = test_pdf_processing()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Enhanced analytics processing test PASSED!")
        print("✅ PDF → Analytics → Excel pipeline working correctly")
    else:
        print("❌ Test failed - check the output above for details")
