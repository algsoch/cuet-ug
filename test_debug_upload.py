#!/usr/bin/env python3

import requests
import time
import os

def test_upload_and_processing():
    """Test upload and processing with server logs"""
    print("🚀 Testing PDF Upload and Processing with Debug")
    print("=" * 60)
    
    # Use port 8002 for the new server
    base_url = "http://localhost:8002"
    
    test_file = "test_file.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return
    
    try:
        # Upload file
        print("📤 Uploading file...")
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/api/upload", files=files, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        result = response.json()
        process_id = result['process_id']
        print(f"✅ Upload successful! Process ID: {process_id}")
        
        # Monitor processing
        print("⏳ Monitoring processing...")
        max_attempts = 20  # Reduced to 20 attempts
        
        for i in range(max_attempts):
            try:
                status_response = requests.get(f"{base_url}/api/status/{process_id}", timeout=10)
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"📊 Attempt {i+1}: Status = {status.get('status', 'unknown')}")
                    
                    if status.get('status') == 'completed':
                        print("✅ Processing completed successfully!")
                        return
                    elif status.get('status') == 'error':
                        print(f"❌ Processing error: {status.get('message', 'Unknown error')}")
                        if 'error' in status:
                            print(f"🔍 Error details: {status['error']}")
                        return
                else:
                    print(f"⚠️  Status check failed: {status_response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Request error: {e}")
            
            time.sleep(3)  # Check every 3 seconds
        
        print("⏰ Processing monitoring timeout reached")
        
    except Exception as e:
        print(f"💥 Exception: {str(e)}")

if __name__ == "__main__":
    test_upload_and_processing()
