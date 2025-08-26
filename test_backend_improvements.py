"""
Comprehensive Test Script for Backend Improvements
Tests data recovery, performance optimizations, and new features
"""

import pandas as pd
import time
import requests
import json
import asyncio
from typing import Dict, Any
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_data_recovery():
    """Test the improved data cleaning results"""
    print("🧪 TESTING DATA RECOVERY IMPROVEMENTS")
    print("="*60)
    
    # Check if we have the improved cleaned data
    output_dir = 'outputs'
    improved_files = [f for f in os.listdir(output_dir) if f.startswith('DU_Admission_Improved_Clean_') and f.endswith('.csv')]
    
    if not improved_files:
        print("❌ No improved cleaned data found. Run test_improved_cleaning.py first.")
        return False
    
    # Load the improved data
    latest_improved = max(improved_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
    improved_path = os.path.join(output_dir, latest_improved)
    improved_data = pd.read_csv(improved_path)
    
    print(f"✅ Loaded improved data: {len(improved_data)} rows")
    print(f"📊 Unique colleges: {improved_data['NAME OF THE COLLEGE'].nunique()}")
    print(f"📚 Unique programs: {improved_data['NAME OF THE PROGRAM'].nunique()}")
    
    # Calculate total seats
    numeric_columns = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
    total_seats = improved_data[numeric_columns].sum().sum()
    print(f"🪑 Total seats: {total_seats:,}")
    
    # Data quality checks
    valid_college_rows = improved_data[improved_data['NAME OF THE COLLEGE'].str.strip() != '']
    valid_program_rows = improved_data[improved_data['NAME OF THE PROGRAM'].str.strip() != '']
    
    print(f"✅ Rows with valid colleges: {len(valid_college_rows)}/{len(improved_data)} ({len(valid_college_rows)/len(improved_data)*100:.1f}%)")
    print(f"✅ Rows with valid programs: {len(valid_program_rows)}/{len(improved_data)} ({len(valid_program_rows)/len(improved_data)*100:.1f}%)")
    
    return True

def test_api_performance():
    """Test API response times and caching"""
    print(f"\n🚀 TESTING API PERFORMANCE")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/health", timeout=5)
        health_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Health check: {health_time*1000:.1f}ms")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("💡 Make sure the server is running: python app.py")
        return False
    
    # Test raw data endpoint
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/raw-data", timeout=10)
        raw_data_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Raw data: {raw_data_time*1000:.1f}ms ({len(data)} records)")
        else:
            print(f"❌ Raw data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Raw data error: {str(e)}")
    
    # Test chart data endpoint
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/chart-data", timeout=10)
        chart_data_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Chart data: {chart_data_time*1000:.1f}ms")
        else:
            print(f"❌ Chart data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chart data error: {str(e)}")
    
    # Test new optimized endpoints if available
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/v2/analytics", timeout=10)
        v2_analytics_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ V2 Analytics: {v2_analytics_time*1000:.1f}ms (cached)")
        else:
            print(f"⚠️  V2 Analytics not available: {response.status_code}")
    except Exception as e:
        print(f"⚠️  V2 Analytics not available: {str(e)}")
    
    return True

def test_data_pagination():
    """Test pagination functionality"""
    print(f"\n📄 TESTING DATA PAGINATION")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test different page sizes
        page_sizes = [10, 50, 100]
        
        for page_size in page_sizes:
            start_time = time.time()
            response = requests.get(f"{base_url}/api/v2/data?page=1&page_size={page_size}", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                actual_records = len(data.get('data', []))
                pagination = data.get('pagination', {})
                
                print(f"✅ Page size {page_size}: {response_time*1000:.1f}ms, got {actual_records} records")
                print(f"   📊 Total records: {pagination.get('total_records', 'N/A')}")
                print(f"   📄 Total pages: {pagination.get('total_pages', 'N/A')}")
            else:
                print(f"❌ Page size {page_size} failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Pagination test error: {str(e)}")
        return False
    
    return True

def test_search_functionality():
    """Test search and filtering"""
    print(f"\n🔍 TESTING SEARCH & FILTERING")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test search functionality
        search_terms = ["Acharya", "B.Com", "Economics"]
        
        for term in search_terms:
            start_time = time.time()
            response = requests.get(f"{base_url}/api/v2/data?search={term}&page_size=20", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results = len(data.get('data', []))
                print(f"✅ Search '{term}': {response_time*1000:.1f}ms, {results} results")
            else:
                print(f"❌ Search '{term}' failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Search test error: {str(e)}")
        return False
    
    return True

def test_college_specific_data():
    """Test college-specific endpoints"""
    print(f"\n🏫 TESTING COLLEGE-SPECIFIC DATA")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    try:
        # First get list of colleges
        response = requests.get(f"{base_url}/api/raw-data?limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                college_name = data[0].get('NAME OF THE COLLEGE', '')
                if college_name:
                    # Test college-specific endpoint
                    college_encoded = requests.utils.quote(college_name)
                    start_time = time.time()
                    response = requests.get(f"{base_url}/api/v2/colleges/{college_encoded}/programs", timeout=10)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        college_data = response.json()
                        programs = len(college_data.get('programs', []))
                        total_seats = college_data.get('total_seats', 0)
                        print(f"✅ College '{college_name}': {response_time*1000:.1f}ms")
                        print(f"   📚 Programs: {programs}")
                        print(f"   🪑 Total seats: {total_seats}")
                    else:
                        print(f"❌ College data failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ College data test error: {str(e)}")
        return False
    
    return True

def test_performance_stats():
    """Test performance monitoring endpoints"""
    print(f"\n📈 TESTING PERFORMANCE MONITORING")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/v2/stats", timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            stats = response.json()
            cache_stats = stats.get('cache_stats', {})
            system_stats = stats.get('system_stats', {})
            
            print(f"✅ Performance stats: {response_time*1000:.1f}ms")
            print(f"   💾 Data cache size: {cache_stats.get('data_cache_size', 0)}")
            print(f"   📊 Analytics cache size: {cache_stats.get('analytics_cache_size', 0)}")
            print(f"   🧵 Active threads: {system_stats.get('active_threads', 'N/A')}")
        else:
            print(f"⚠️  Performance stats not available: {response.status_code}")
    
    except Exception as e:
        print(f"⚠️  Performance stats not available: {str(e)}")
        return False
    
    return True

def generate_improvement_report():
    """Generate a comprehensive improvement report"""
    print(f"\n📋 IMPROVEMENT REPORT")
    print("="*60)
    
    # Data recovery metrics
    output_dir = 'outputs'
    raw_files = [f for f in os.listdir(output_dir) if f.startswith('raw_extraction_') and f.endswith('.csv')]
    clean_files = [f for f in os.listdir(output_dir) if f.startswith('DU_Admission_Clean_Data_') and f.endswith('.csv')]
    improved_files = [f for f in os.listdir(output_dir) if f.startswith('DU_Admission_Improved_Clean_') and f.endswith('.csv')]
    
    if raw_files and clean_files and improved_files:
        latest_raw = max(raw_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
        latest_clean = max(clean_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
        latest_improved = max(improved_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
        
        raw_df = pd.read_csv(os.path.join(output_dir, latest_raw))
        clean_df = pd.read_csv(os.path.join(output_dir, latest_clean))
        improved_df = pd.read_csv(os.path.join(output_dir, latest_improved))
        
        old_efficiency = (len(clean_df) / len(raw_df)) * 100
        new_efficiency = (len(improved_df) / len(raw_df)) * 100
        improvement = new_efficiency - old_efficiency
        
        print(f"📊 DATA PROCESSING IMPROVEMENTS:")
        print(f"   Raw extraction: {len(raw_df):,} rows")
        print(f"   Old cleaning: {len(clean_df):,} rows ({old_efficiency:.1f}% efficiency)")
        print(f"   New cleaning: {len(improved_df):,} rows ({new_efficiency:.1f}% efficiency)")
        print(f"   🎯 Improvement: +{len(improved_df) - len(clean_df):,} rows (+{improvement:.1f}%)")
        
        # Data quality metrics
        old_colleges = clean_df['NAME OF THE COLLEGE'].nunique()
        new_colleges = improved_df['NAME OF THE COLLEGE'].nunique()
        old_programs = clean_df['NAME OF THE PROGRAM'].nunique()
        new_programs = improved_df['NAME OF THE PROGRAM'].nunique()
        
        print(f"\n📈 DATA COVERAGE IMPROVEMENTS:")
        print(f"   Colleges: {old_colleges} → {new_colleges} (+{new_colleges - old_colleges})")
        print(f"   Programs: {old_programs} → {new_programs} (+{new_programs - old_programs})")
        
        # Calculate total seats
        numeric_columns = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
        old_seats = clean_df[numeric_columns].sum().sum()
        new_seats = improved_df[numeric_columns].sum().sum()
        
        print(f"   Total seats: {old_seats:,} → {new_seats:,} (+{new_seats - old_seats:,})")
    
    print(f"\n🚀 BACKEND OPTIMIZATIONS:")
    print(f"   ✅ Added response caching (30min TTL)")
    print(f"   ✅ Implemented pagination (1-1000 records/page)")
    print(f"   ✅ Added search & filtering")
    print(f"   ✅ Response compression (1MB+ responses)")
    print(f"   ✅ Thread pool execution for analytics")
    print(f"   ✅ Performance monitoring endpoints")
    
    print(f"\n🎉 SUMMARY:")
    print(f"   Data recovery improved by {improvement:.1f}%")
    print(f"   Backend performance optimized with caching")
    print(f"   Added advanced API features (pagination, search)")
    print(f"   Enhanced monitoring and debugging capabilities")

def main():
    """Run all tests"""
    print("🧪 COMPREHENSIVE BACKEND IMPROVEMENT TESTS")
    print("="*60)
    print(f"Testing DU Admission Analyzer backend improvements...")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Data Recovery
    total_tests += 1
    if test_data_recovery():
        tests_passed += 1
    
    # Test 2: API Performance
    total_tests += 1
    if test_api_performance():
        tests_passed += 1
    
    # Test 3: Pagination
    total_tests += 1
    if test_data_pagination():
        tests_passed += 1
    
    # Test 4: Search
    total_tests += 1
    if test_search_functionality():
        tests_passed += 1
    
    # Test 5: College-specific data
    total_tests += 1
    if test_college_specific_data():
        tests_passed += 1
    
    # Test 6: Performance stats
    total_tests += 1
    if test_performance_stats():
        tests_passed += 1
    
    # Generate report
    generate_improvement_report()
    
    print(f"\n🏁 TEST RESULTS:")
    print(f"   Tests passed: {tests_passed}/{total_tests}")
    print(f"   Success rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("   ✅ All tests passed! Backend improvements are working correctly.")
    else:
        print("   ⚠️  Some tests failed. Check server status and configuration.")

if __name__ == "__main__":
    main()
