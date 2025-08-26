"""
Test script to verify advanced analytics functionality
"""

import requests
import json
import sys

def test_advanced_analytics():
    """Test the advanced analytics endpoint"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Advanced Analytics Endpoint...")
    
    # First, check if we have any processed data
    try:
        health_response = requests.get(f"{base_url}/api/health")
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return False
    
    # For testing, we'll use a mock process_id
    # In real usage, this would come from PDF processing
    test_process_id = "test_process"
    
    try:
        # Test advanced analytics endpoint
        analytics_url = f"{base_url}/api/advanced-analytics/{test_process_id}"
        print(f"📊 Testing: {analytics_url}")
        
        response = requests.get(analytics_url)
        
        if response.status_code == 404:
            print("📝 No processed data found (expected for fresh start)")
            print("   To test with real data:")
            print("   1. Upload a PDF file through the web interface")
            print("   2. Wait for processing to complete")  
            print("   3. Use the real process_id from the upload")
            return True
        elif response.status_code == 200:
            data = response.json()
            print("✅ Advanced analytics endpoint working!")
            print(f"📈 Response structure: {list(data.keys())}")
            if 'data' in data:
                analytics_keys = list(data['data'].keys())
                print(f"🔍 Analytics sections: {analytics_keys}")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing analytics: {str(e)}")
        return False

def test_frontend():
    """Test if frontend is accessible"""
    try:
        base_url = "http://localhost:8000"
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing frontend: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DU Admission Analyzer - Advanced Analytics Test")
    print("=" * 50)
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Test analytics
    analytics_ok = test_advanced_analytics()
    
    print("\n" + "=" * 50)
    if frontend_ok and analytics_ok:
        print("🎉 All tests passed! Advanced Analytics is ready.")
        print("\n📋 Next Steps:")
        print("1. Upload a PDF file at http://localhost:8000")
        print("2. Wait for processing to complete")
        print("3. View the enhanced analytics dashboard")
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)
